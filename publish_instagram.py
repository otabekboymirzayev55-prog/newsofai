"""Explicit Instagram Login Reel publishing with durable deduplication and recovery."""
import argparse
from datetime import datetime
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

from instagram import instagram_handle, validate_pack
from social_config import load_env


class InstagramClient:
    def __init__(self):
        self.token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
        self.user = os.environ.get('INSTAGRAM_USER_ID', '')
        version = os.environ.get('INSTAGRAM_GRAPH_VERSION', '')
        if not self.token or not self.user.isdigit() or not re.fullmatch(r'v\d+\.0', version):
            raise ValueError('Configure INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID and INSTAGRAM_GRAPH_VERSION')
        self.base = f'https://graph.instagram.com/{version}'

    def call(self, path, fields=None, post=False):
        if not re.fullmatch(r'[0-9]+(?:/(?:media|media_publish))?', path):
            raise ValueError('Invalid Instagram endpoint')
        payload = urllib.parse.urlencode(fields or {}).encode()
        url = self.base + '/' + path
        if not post:
            url += '?' + payload.decode()
        req = urllib.request.Request(url, data=payload if post else None, headers={
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read(1_000_001))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f'Instagram HTTP {exc.code}; check token, permissions and media status') from None
        except (urllib.error.URLError, TimeoutError, ValueError):
            raise RuntimeError('Instagram request failed; inspect saved state before retrying publication') from None
        if not isinstance(data, dict) or 'error' in data:
            raise RuntimeError('Instagram rejected request')
        return data

    def check_account(self, expected):
        profile = self.call(self.user, {'fields': 'id,username'})
        if instagram_handle(profile.get('username', '')) != expected:
            raise ValueError('Configured token belongs to a different Instagram account')
        return expected


def public_video_url(value):
    parts = urllib.parse.urlsplit(value)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or parts.fragment:
        raise ValueError('Use a public HTTPS video URL without credentials')
    if parts.hostname.lower() == 'localhost' or parts.hostname.endswith('.local'):
        raise ValueError('Instagram cannot download local media')
    try:
        if not ipaddress.ip_address(parts.hostname).is_global:
            raise ValueError('Use a public media host')
    except ValueError as exc:
        # Domain names are resolved by Instagram; literal IPs must be globally routable.
        if ':' in parts.hostname or re.fullmatch(r'[0-9.]+', parts.hostname):
            raise ValueError('Use a public media host') from exc
    return value


def load_publication(pack_dir, video):
    root, video = Path(pack_dir), Path(video)
    metadata = json.loads((root / 'pack.json').read_text(encoding='utf-8'))
    validate_pack(metadata)
    if metadata.get('demo') or metadata.get('account') != instagram_handle():
        raise ValueError('Cannot publish demo content or content for another account')
    source_url = metadata['source']['url']
    public_video_url(source_url)
    caption = (root / 'caption.txt').read_text(encoding='utf-8').strip()
    if not caption or len(caption) > 2200:
        raise ValueError('Invalid caption')
    manifest = json.loads(video.with_suffix(video.suffix + '.manifest.json').read_text(encoding='utf-8'))
    if manifest.get('final') is not True:
        raise ValueError('Render with --final before publishing')
    for key, file in [('video_sha256', video), ('pack_sha256', root / 'pack.json'),
                      ('caption_sha256', root / 'caption.txt')]:
        if manifest.get(key) != hashlib.sha256(file.read_bytes()).hexdigest():
            raise ValueError('Publication files changed after final render; render and review again')
    return metadata, caption


def open_state(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.execute('''CREATE TABLE IF NOT EXISTS instagram_publications (
        account TEXT, source TEXT, status TEXT, container TEXT, media TEXT,
        claimed_at REAL, PRIMARY KEY(account, source))''')
    db.commit()
    return db


def publish(db, client, metadata, caption, video_url):
    account = instagram_handle()
    public_video_url(video_url)
    client.check_account(account)
    source = metadata['source']['url']
    # One claim before every possible remote mutation. Never auto-retry ambiguous writes.
    with db:
        db.execute('BEGIN IMMEDIATE')
        existing = db.execute('SELECT status FROM instagram_publications WHERE account=? AND source=?',
                              (account, source)).fetchone()
        if existing:
            return existing[0]
        midnight = datetime.now(ZoneInfo('Asia/Tashkent')).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        count = db.execute('SELECT COUNT(*) FROM instagram_publications WHERE account=? AND claimed_at>=?',
                           (account, midnight)).fetchone()[0]
        if count >= 15:
            raise RuntimeError('Tashkent daily limit reached (including pending attempts)')
        db.execute('INSERT INTO instagram_publications VALUES (?,?,?,?,?,?)',
                   (account, source, 'creating', None, None, time.time()))
    container = client.call(client.user + '/media', {'media_type': 'REELS', 'video_url': video_url,
                                                     'caption': caption, 'share_to_feed': 'true'}, post=True)['id']
    if not str(container).isdigit():
        raise RuntimeError('Instagram returned an invalid container ID')
    with db:
        db.execute('UPDATE instagram_publications SET status=?,container=? WHERE account=? AND source=?',
                   ('processing', container, account, source))
    return resume(db, client, source)


def resume(db, client, source):
    account = instagram_handle()
    client.check_account(account)
    # Serialize transitions so two workers cannot send media_publish for one container.
    with db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT status,container FROM instagram_publications WHERE account=? AND source=?',
                         (account, source)).fetchone()
        if not row:
            raise ValueError('No stored publication for this source')
        status, container = row
        if status != 'processing':
            return status
        remote = client.call(str(container), {'fields': 'status_code'}).get('status_code')
        if remote == 'IN_PROGRESS':
            return 'processing'
        if remote == 'PUBLISHED':
            db.execute('UPDATE instagram_publications SET status=? WHERE account=? AND source=?',
                       ('published', account, source))
            return 'published'
        if remote != 'FINISHED':
            raise RuntimeError('Container is not publishable; inspect Instagram before taking further action')
        db.execute('UPDATE instagram_publications SET status=? WHERE account=? AND source=?',
                   ('publishing', account, source))
    # Ambiguous failures remain publishing; the next run cannot send again.
    result = client.call(client.user + '/media_publish', {'creation_id': container}, post=True)
    media = result.get('id')
    if not str(media).isdigit():
        raise RuntimeError('Instagram did not confirm publication; check the account')
    with db:
        db.execute('UPDATE instagram_publications SET status=?,media=? WHERE account=? AND source=?',
                   ('published', media, account, source))
    return 'published'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', help='Explicit private social.env, never printed')
    parser.add_argument('--pack-dir')
    parser.add_argument('--video')
    parser.add_argument('--video-url', help='Public URL serving this exact final MP4')
    parser.add_argument('--state', default='.local/instagram-publications.sqlite3')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--check-account', action='store_true')
    action.add_argument('--publish', action='store_true', help='Explicitly create/publish this Reel')
    action.add_argument('--resume', metavar='SOURCE_URL', help='Check one processing container and publish if ready')
    args = parser.parse_args()
    try:
        load_env(args.env_file)
        if args.check_account:
            print('Instagram account verified: ' + InstagramClient().check_account(instagram_handle()))
            return 0
        if args.resume:
            with open_state(args.state) as db:
                print('Publication state: ' + resume(db, InstagramClient(), args.resume))
            return 0
        if not args.pack_dir or not args.video:
            parser.error('--pack-dir and --video are required for publication validation')
        metadata, caption = load_publication(args.pack_dir, args.video)
        if not args.publish:
            print('Local final files validated. No API calls or publication. Use --publish with a public --video-url to send.')
            return 0
        if not args.video_url:
            parser.error('--publish requires --video-url')
        with open_state(args.state) as db:
            print('Publication state: ' + publish(db, InstagramClient(), metadata, caption, args.video_url))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, sqlite3.Error):
        print('Publication stopped. Check configuration, final manifest and durable state. Never clear pending state to retry an uncertain post.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

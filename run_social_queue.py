"""Publish due final Reel jobs from an explicit timezone-aware schedule."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3

from publish_instagram import InstagramClient, load_publication, open_state, publish, resume
from social_config import load_env


def due_jobs(path, now=None):
    source = Path(path).resolve()
    jobs = json.loads(source.read_text(encoding='utf-8'))
    if not isinstance(jobs, list) or len(jobs) > 500:
        raise ValueError('Expected at most 500 queue jobs')
    now = now or datetime.now(timezone.utc)
    due = []
    for job in jobs:
        scheduled = datetime.fromisoformat(job['publish_at'].replace('Z', '+00:00'))
        if scheduled.tzinfo is None:
            raise ValueError('Queue times must include a timezone, e.g. +05:00')
        for key in ('pack_dir', 'video', 'video_url'):
            if not isinstance(job[key], str) or not job[key]:
                raise ValueError('Incomplete queue job')
        if scheduled <= now:
            due.append({**job, 'pack_dir': str(source.parent / job['pack_dir']),
                        'video': str(source.parent / job['video'])})
    return due


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('queue')
    parser.add_argument('--env-file')
    parser.add_argument('--state', default='.local/instagram-publications.sqlite3')
    parser.add_argument('--publish', action='store_true', help='Send due jobs; default only validates local final files')
    args = parser.parse_args()
    try:
        load_env(args.env_file)
        jobs = due_jobs(args.queue)
        failures = 0
        client = InstagramClient() if args.publish else None
        with open_state(args.state) as db:
            for i, job in enumerate(jobs, 1):
                try:
                    metadata, caption = load_publication(job['pack_dir'], job['video'])
                    if not args.publish:
                        print(f'Job {i}: local final files validated, not published')
                        continue
                    state = publish(db, client, metadata, caption, job['video_url'])
                    if state == 'processing':
                        state = resume(db, client, metadata['source']['url'])
                    print(f'Job {i}: {state}')
                    if state in ('creating', 'publishing'):
                        failures += 1
                except (OSError, ValueError, KeyError, RuntimeError):
                    print(f'Job {i}: stopped; inspect configuration and stored state')
                    failures += 1
        return 1 if failures else 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, sqlite3.Error):
        print('Queue stopped. Check timezone-aware schedule, configuration and local final files.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

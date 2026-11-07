"""Check decoded motion, publish local review metadata and package approved files.

This does not schedule or upload Instagram posts, or change any VPS service.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import news_pool
from batch_news.catalog import build

OUT = ROOT / 'media/batches/2026-11-07'


def motion(video):
    differences = []
    for shot in range(4):
        samples = []
        for offset in (1, 3.5):
            raw = subprocess.check_output([
                'ffmpeg', '-v', 'error', '-threads', '2', '-ss', str(shot * 4.5 + offset),
                '-i', str(video), '-frames:v', '1', '-vf',
                'crop=920:550:80:950,scale=230:138', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
            samples.append(np.frombuffer(raw, dtype=np.uint8).astype(np.float32))
        if len(samples[0]) != 230 * 138 * 3 or len(samples[1]) != len(samples[0]):
            raise RuntimeError('Motion sample could not be decoded')
        difference = float(np.abs(samples[0] - samples[1]).mean())
        if difference < .5:
            raise RuntimeError(f'Inspect unexpectedly static visual region in shot {shot + 1}')
        differences.append(round(difference, 4))
    return differences


def main():
    stories = json.loads((ROOT / 'batch_news/stories.json').read_text())
    reserves = json.loads((OUT / 'reserve.json').read_text())
    if len(stories) != 7 or len(reserves) != 10:
        raise RuntimeError('Expected exactly seven commissioned films and ten saved reserves')
    pool = news_pool.read(ROOT / 'media/news-pool.json')
    reports = []
    for story in stories:
        folder = OUT / story['id']
        video = folder / 'video.mp4'
        report = json.loads((folder / 'production.json').read_text())
        if report['status'] != 'technical_checks_passed' or not report['visual_review'].startswith('assistant inspected'):
            raise RuntimeError('Finish actual visual and technical review first: ' + story['id'])
        if report['sha256'] != hashlib.sha256(video.read_bytes()).hexdigest():
            raise RuntimeError('Video changed after review: ' + story['id'])
        if json.loads((folder / 'story.json').read_text()) != story:
            raise RuntimeError('Export does not match commissioned script')
        decoded = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '2', '-i', str(video),
                                  '-f', 'null', '-'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        if decoded.stderr.strip():
            raise RuntimeError('Full-decode errors require inspection: ' + story['id'])
        report['full_decode'] = 'passed: all video and audio decoded without FFmpeg errors'
        report['visual_region_motion_mad_0_255'] = motion(video)
        report['motion_check_note'] = 'Mean absolute RGB change between 1s and 3.5s in each shot, excluding headline/footer. Checks motion presence, not subjective animation quality.'
        (folder / 'production.json').write_text(json.dumps(report, indent=2) + '\n')
        for candidate in pool['candidates']:
            if candidate['id'] == story['id']:
                if candidate.get('status') not in ('scheduled', 'published'):
                    candidate.update(status='video_ready', scheduled=False)
                candidate.update(video=str(video.relative_to(ROOT)), sha256=report['sha256'])
        reports.append({'id': story['id'], 'video': str(video.relative_to(ROOT)),
                        'sha256': report['sha256'], 'bytes': report['bytes'],
                        'motion_by_shot': report['visual_region_motion_mad_0_255']})
        print('DELIVERY CHECKED', story['id'], flush=True)
    news_pool.save(ROOT / 'media/news-pool.json', pool)
    build()
    held = [c['id'] for c in pool['candidates'] if c['id'] in {s['id'] for s in stories} and c.get('publication_hold')]
    manifest = {'checked_on': '2026-11-07', 'ready_videos': len(reports), 'saved_reserves': 10,
                'publication_hold': bool(held), 'held_video_ids': held,
                'editorial_status': 'needs_format_revision' if held else 'reviewed',
                'publish_ready_videos': len(reports)-len(held),
                'scheduled': False, 'published': False, 'telegram_vps_deployed': False,
                'telegram_blocker': 'No server host or authenticated SSH access in this session',
                'source_refresh_before_publication_required': True, 'videos': reports}
    (OUT / 'delivery.json').write_text(json.dumps(manifest, indent=2) + '\n')
    archive = ROOT / '.local/mirabilis-7-video-2026-11-07.zip'
    paths = sorted(p for p in OUT.rglob('*') if p.is_file())
    paths += [ROOT / name for name in ['media/news-pool.json', 'TELEGRAM_EDITORIAL.md',
                                      'batch_news/README.md', 'NEWS_SELECTION.md', 'INSTAGRAM_FORMATS.md']]
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as bundle:
        bundle.writestr('BOSHLASH.html', '<!doctype html><meta charset="utf-8"><title>Mirabilis On — 7 video</title><meta http-equiv="refresh" content="0;url=media/batches/2026-11-07/index.html"><a href="media/batches/2026-11-07/index.html">7 ta video katalogini ochish</a>')
        for path in paths:
            bundle.write(path, path.relative_to(ROOT))
    print('ARCHIVE', archive, archive.stat().st_size, flush=True)
    if archive.stat().st_size > 32 * 1024 * 1024:
        print('Archive exceeds 32 MiB; individual video links remain available.', flush=True)
    from batch_news.run_batch import checkpoint
    checkpoint('completed')


if __name__ == '__main__':
    main()

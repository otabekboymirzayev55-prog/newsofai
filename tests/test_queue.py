from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from run_social_queue import due_jobs


class QueueTests(unittest.TestCase):
    def test_tashkent_schedule_and_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'queue.json'
            job = {'publish_at': '2026-11-05T19:00:00+05:00', 'pack_dir': 'pack',
                   'video': 'pack/final.mp4', 'video_url': 'https://example.com/final.mp4'}
            path.write_text(json.dumps([job]), encoding='utf-8')
            self.assertEqual(due_jobs(path, datetime(2026, 11, 5, 13, 59, tzinfo=timezone.utc)), [])
            due = due_jobs(path, datetime(2026, 11, 5, 14, 0, tzinfo=timezone.utc))
            self.assertEqual(len(due), 1)
            self.assertEqual(Path(due[0]['video']), Path(tmp) / 'pack/final.mp4')

    def test_rejects_ambiguous_local_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'queue.json'
            path.write_text(json.dumps([{'publish_at': '2026-11-05T19:00:00'}]), encoding='utf-8')
            with self.assertRaises(ValueError):
                due_jobs(path)

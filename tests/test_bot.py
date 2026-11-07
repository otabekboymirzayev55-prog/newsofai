import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import bot


class BotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = bot.open_state(str(Path(self.tmp.name) / 'state.sqlite3'))
        self.article = bot.Article('AI news', 'https://example.com/news', 'Facts', datetime.now(timezone.utc))
        self.env = patch.dict(os.environ, {'POST_INTERVAL_HOURS': '0.001', 'FEED_URLS': 'https://example.com/feed'})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.db.close()
        self.tmp.cleanup()

    def cycle(self, dry=False, send_error=None):
        selection = bot.news_selection.Selection(self.article, 'example-important-event-2026-11-07',
                                                {'primary_url': self.article.url}, 'Verified facts')
        with patch('bot.request', return_value=b'<rss/>'), patch('bot.parse_feed', return_value=[self.article]), \
             patch('bot.news_selection.select', return_value=selection), \
             patch('bot.generate_post', return_value='Uzbek post'), patch('bot.send_post', side_effect=send_error) as send:
            bot.run_once(self.db, dry)
            return send.call_count

    def test_rss_and_atom(self):
        rss = b'<rss><channel><item><title>AI</title><link>https://example.com/a</link><pubDate>Thu, 05 Nov 2026 01:00:00 GMT</pubDate></item></channel></rss>'
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>AI</title><link href="https://example.com/b"/><updated>2026-11-05T01:00:00Z</updated></entry></feed>'
        self.assertEqual(bot.parse_feed(rss)[0].url, 'https://example.com/a')
        self.assertEqual(bot.parse_feed(atom)[0].url, 'https://example.com/b')

    def test_post_once_then_deduplicate(self):
        self.assertEqual(self.cycle(), 1)
        self.assertEqual(self.cycle(), 0)
        self.assertEqual(self.db.execute('SELECT status FROM posts').fetchone()[0], 'sent')

    def test_default_ninety_minute_boundary(self):
        # An explicit VPS setting overrides defaults; test the unset default.
        with patch.dict(os.environ):
            os.environ.pop('POST_INTERVAL_HOURS', None)
            for status in ('sent', 'pending'):
                with self.subTest(status=status):
                    self.db.execute('DELETE FROM posts')
                    self.db.execute('DELETE FROM news_events')
                    self.db.execute('INSERT INTO posts VALUES (?, ?, ?, ?)',
                                    ('previous', 'https://example.com/previous', status, 10000))
                    self.db.commit()
                    with patch('bot.time.time', return_value=15399):
                        self.assertEqual(self.cycle(), 0)
                    with patch('bot.time.time', return_value=15400):
                        self.assertEqual(self.cycle(), 1)

    def test_dry_run_does_not_send_or_record(self):
        with patch('builtins.print'):
            self.assertEqual(self.cycle(dry=True), 0)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM posts').fetchone()[0], 0)

    def test_daily_limit(self):
        for i in range(18):
            self.db.execute('INSERT INTO posts VALUES (?, ?, ?, ?)', (str(i), str(i), 'sent', bot.time.time() - 60))
        self.db.commit()
        self.assertEqual(self.cycle(), 0)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM posts').fetchone()[0], 18)

    def test_eighteenth_post_allowed_after_interval(self):
        for i in range(17):
            self.db.execute('INSERT INTO posts VALUES (?, ?, ?, ?)',
                            (str(i), str(i), 'sent', bot.time.time() - 60))
        self.db.commit()
        self.assertEqual(self.cycle(), 1)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM posts').fetchone()[0], 18)

    def test_uncertain_send_stays_pending(self):
        with self.assertRaises(RuntimeError):
            self.cycle(send_error=RuntimeError('Connection failed'))
        self.assertEqual(self.db.execute('SELECT status FROM posts').fetchone()[0], 'pending')
        self.assertEqual(self.cycle(), 0)

    def test_ai_generation(self):
        response = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': 'Yangi AI modeli e’lon qilindi.'}]}}]}
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}), patch('bot.request', return_value=json.dumps(response).encode()):
            text = bot.generate_post(self.article)
        self.assertIn('Yangi AI', text)
        self.assertTrue(text.endswith('Manba: https://example.com/news'))

    def test_feed_failure_is_error(self):
        with patch('bot.request', side_effect=RuntimeError('Blocked')):
            with self.assertRaises(RuntimeError):
                bot.run_once(self.db)


if __name__ == '__main__':
    unittest.main()

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import bot
import news_selection as editorial


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = bot.open_state(str(Path(self.tmp.name) / 'state.db'))
        self.now = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)
        self.article = bot.Article('Major research advance', 'https://publisher.example/story',
                                   'Research has important implications.', self.now - timedelta(days=10))
        self.primary = 'https://research.example/announcement'
        self.text = ('Announcement date: October 28, 2026. Researchers demonstrated a new method. '
                     'It remains an early laboratory result, not a deployed medical treatment. ')
        self.fetch = Mock(side_effect=lambda url: (
            ('<p>' + self.text + '</p><a href="' + self.primary + '">Original study</a>').encode()
            if url == self.article.url else ('<p>' + self.text + '</p>').encode()))
        self.review = dict(approved=True, primary_is_original=True,
                           event_key='research-method-announcement-2026-10-28', event_date='2026-10-28',
                           event_date_quote='Announcement date: October 28, 2026.', impact='Muhim imkoniyat.',
                           limitations='Laboratoriya natijasi.', facts=[dict(text='Yangi usul namoyish qilindi.',
                           quote='Researchers demonstrated a new method.')])

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def choose(self, articles=None, review=None, locator=None):
        complete = Mock(side_effect=[json.dumps({'ranked': [0]}),
                                     json.dumps({'primary_url': self.primary} if locator is None else locator),
                                     json.dumps(self.review if review is None else review)])
        result = editorial.select(self.db, articles or [self.article], self.now,
                                  self.fetch, complete, bot.Article)
        return result, complete

    def test_old_important_story_survives_and_primary_is_retrieved(self):
        new = bot.Article('Minor update', 'https://publisher.example/minor', 'Cosmetic change', self.now)
        complete = Mock(side_effect=[json.dumps({'ranked': [1]}),
                                     json.dumps({'primary_url': self.primary}), json.dumps(self.review)])
        selected = editorial.select(self.db, [new, self.article], self.now, self.fetch, complete, bot.Article)
        self.assertEqual(selected.article.url, self.article.url)
        self.assertEqual(self.fetch.call_args_list[-1].args[0], self.primary)
        self.assertNotIn('Cosmetic change', selected.context)

    def test_fabricated_primary_quote_rejected(self):
        review = {**self.review, 'facts': [{'text': 'Invented', 'quote': 'This is not in the primary source.'}]}
        self.assertIsNone(self.choose(review=review)[0])

    def test_old_event_in_recent_article_rejected(self):
        review = {**self.review, 'event_date': '2026-09-01'}
        self.assertIsNone(self.choose(review=review)[0])

    def test_unobserved_primary_link_never_fetched(self):
        selected, complete = self.choose(locator={'primary_url': 'https://invented.example/study'})
        self.assertIsNone(selected)
        self.assertEqual(self.fetch.call_count, 1)
        self.assertEqual(complete.call_count, 2)

    def test_same_event_different_url_is_rejected(self):
        self.db.execute('INSERT INTO news_events VALUES (?, ?, ?, ?, ?)',
                        (self.review['event_key'], 'old-id', 'Same event elsewhere', '{}', 1))
        self.db.commit()
        self.assertIsNone(self.choose()[0])

    def test_insufficient_news_and_failed_calls_have_cooldown(self):
        for fails in (False, True):
            self.db.execute('DELETE FROM editorial_runs')
            self.db.commit()
            complete = Mock(side_effect=RuntimeError('Provider failed')) if fails else Mock(return_value='{"ranked":[]}')
            with patch('news_selection.time.time', return_value=10000):
                if fails:
                    with self.assertRaises(RuntimeError):
                        editorial.select(self.db, [self.article], self.now, self.fetch, complete, bot.Article)
                else:
                    self.assertIsNone(editorial.select(self.db, [self.article], self.now, self.fetch, complete, bot.Article))
            with patch('news_selection.time.time', return_value=10300):
                self.assertIsNone(editorial.select(self.db, [self.article], self.now, self.fetch, complete, bot.Article))
            self.assertEqual(complete.call_count, 1)

    def test_tracking_url_and_preexisting_state_preserved(self):
        self.db.execute('INSERT INTO posts VALUES (?, ?, ?, ?)',
                        ('legacy-id', self.article.url + '?utm_source=rss', 'pending', 1))
        self.db.commit()
        complete = Mock()
        self.assertIsNone(editorial.select(self.db, [self.article], self.now, self.fetch, complete, bot.Article))
        complete.assert_not_called()
        self.assertEqual(self.db.execute('SELECT id,status FROM posts').fetchone(), ('legacy-id', 'pending'))

    def test_fourteen_day_cache_and_age_buckets(self):
        articles = [bot.Article('News', f'https://publisher.example/{i}', 'Summary',
                               self.now - timedelta(days=i)) for i in range(16)]
        complete = Mock(return_value='{"ranked":[]}')
        editorial.select(self.db, articles, self.now, self.fetch, complete, bot.Article)
        payload = complete.call_args.args[0]
        self.assertIn('2026-10-24', payload)
        self.assertNotIn('https://publisher.example/15"', payload)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM news_articles').fetchone()[0], 15)

    def test_private_source_urls_rejected(self):
        for url in ['https://127.0.0.1/a', 'https://[::1]/a', 'http://example.com',
                    'https://localhost/a', 'https://x.internal/a', 'https://user:pass@example.com/a']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                editorial.canonical_url(url)

    def test_event_claim_stays_pending_on_uncertain_telegram_send(self):
        selected, _ = self.choose()
        with patch.dict('os.environ', {'POST_INTERVAL_HOURS': '0.001'}), \
                patch('bot.request', return_value=b'<rss/>'), \
                patch('bot.parse_feed', return_value=[self.article]), \
                patch('bot.news_selection.select', return_value=selected), \
                patch('bot.generate_post', return_value='Verified post'), \
                patch('bot.send_post', side_effect=RuntimeError('Timeout')):
            with self.assertRaises(RuntimeError):
                bot.run_once(self.db)
        self.assertEqual(self.db.execute('SELECT status FROM posts').fetchone()[0], 'pending')
        self.assertEqual(self.db.execute('SELECT event_key FROM news_events').fetchone()[0], selected.event_key)

    def test_full_bot_flow_uses_reviewed_facts_and_records_audit(self):
        outputs = iter([{'ranked': [0]}, {'primary_url': self.primary}, self.review,
                        'Yangi usul namoyish qilindi. Hozircha laboratoriya natijasi.'])
        def request(url, payload=None, headers=None):
            if payload is None:
                return b'<rss/>'
            value = next(outputs)
            text = json.dumps(value) if isinstance(value, dict) else value
            return json.dumps({'candidates': [{'finishReason': 'STOP',
                              'content': {'parts': [{'text': text}]}}]}).encode()
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key', 'POST_INTERVAL_HOURS': '1.5'}), \
                patch('bot.request', side_effect=request), \
                patch('bot.fetch_source', side_effect=self.fetch), \
                patch('bot.parse_feed', return_value=[self.article]), \
                patch('bot.datetime') as clock, patch('bot.send_post') as send:
            clock.now.return_value = self.now
            bot.run_once(self.db)
        send.assert_called_once()
        self.assertIn('Asl manba: ' + self.primary, send.call_args.args[0])
        self.assertEqual(self.db.execute('SELECT status FROM posts').fetchone()[0], 'sent')
        audit = json.loads(self.db.execute('SELECT details FROM editorial_runs').fetchone()[0])
        self.assertEqual(audit['selected']['primary_url'], self.primary)


if __name__ == '__main__':
    unittest.main()

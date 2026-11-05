import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bot
import instagram


class InstagramTests(unittest.TestCase):
    def setUp(self):
        examples = Path(instagram.__file__).with_name('examples')
        self.pack = json.loads((examples / 'instagram-pack.json').read_text(encoding='utf-8'))
        self.article = instagram.load_article(examples / 'instagram-source.json')

    def test_pack_exports_source_and_timed_subtitles_without_telegram(self):
        with tempfile.TemporaryDirectory() as tmp, patch('bot.send_post') as send:
            target = instagram.save_pack(tmp, self.article, self.pack, demo=True)
            saved = json.loads((target / 'pack.json').read_text(encoding='utf-8'))
            self.assertEqual(saved['status'], 'needs_review')
            self.assertEqual(saved['account'], instagram.instagram_handle())
            self.assertTrue(saved['demo'])
            self.assertEqual(saved['source']['url'], self.article.url)
            self.assertIn(self.article.url, (target / 'caption.txt').read_text(encoding='utf-8'))
            subtitles = (target / 'subtitles.srt').read_text(encoding='utf-8')
            self.assertIn('00:00:00,000 --> 00:00:02,000', subtitles)
            self.assertIn('00:00:20,000 --> 00:00:26,000', subtitles)
            self.assertFalse(list(Path(tmp).rglob('*.sqlite3')))
            send.assert_not_called()

    def test_duplicate_preserves_reviewed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = instagram.save_pack(tmp, self.article, self.pack)
            (target / 'caption.txt').write_text('Edited by reviewer', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                instagram.save_pack(tmp, self.article, self.pack)
            self.assertEqual((target / 'caption.txt').read_text(encoding='utf-8'), 'Edited by reviewer')

    def test_rejects_invalid_ai_shapes_and_timings(self):
        for field, replacement in [('scenes', []), ('music', None), ('checks', []), ('carousel', ['one']), ('caption', 'x' * 1201)]:
            data = copy.deepcopy(self.pack)
            data[field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                instagram.validate_pack(data)
        for duration in [True, 0, 9, '6']:
            data = copy.deepcopy(self.pack)
            data['scenes'][1]['duration'] = duration
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                instagram.validate_pack(data)

    def test_gemini_json_and_truncated_response(self):
        response = {'candidates': [{'finishReason': 'STOP', 'content': {
            'parts': [{'text': json.dumps(self.pack)}]}}]}
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-only'}), \
                patch('instagram.request', return_value=json.dumps(response).encode()) as req:
            generated = instagram.generate_pack(self.article)
            self.assertEqual(generated['title'], self.pack['title'])
            self.assertEqual(req.call_args.args[1]['generationConfig']['responseMimeType'], 'application/json')
            self.assertIn(instagram.instagram_handle(), req.call_args.args[1]['contents'][0]['parts'][0]['text'])
            response['candidates'][0]['finishReason'] = 'MAX_TOKENS'
            req.return_value = json.dumps(response).encode()
            with self.assertRaises(RuntimeError):
                instagram.generate_pack(self.article)

    def test_offline_demo_never_calls_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch('instagram.request') as network, \
                patch('sys.argv', ['instagram.py', '--demo', '--out', tmp]):
            self.assertEqual(instagram.main(), 0)
            network.assert_not_called()

    def test_fresh_articles_excludes_stale_and_future_sources(self):
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        articles = [bot.Article('Title', 'https://example.com/' + str(days), 'Summary', now + timedelta(days=days))
                    for days in [-4, -1, 1]]
        with patch('instagram.request', return_value=b'<rss/>'), \
                patch('instagram.parse_feed', return_value=articles), \
                patch.dict(os.environ, {'FEED_URLS': 'https://example.com/feed'}):
            self.assertEqual(instagram.fresh_articles(), [articles[1]])

    def test_rejects_caption_overflow_with_source(self):
        article = bot.Article('Title', 'https://example.com/' + 'x' * 2000, 'Summary', self.article.published)
        pack = copy.deepcopy(self.pack)
        pack['caption'] = 'x' * 1200
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            instagram.save_pack(tmp, article, pack)

    def test_account_configuration_and_invalid_values(self):
        with patch.dict(os.environ, {'INSTAGRAM_HANDLE': '@Safeguard_On'}):
            self.assertEqual(instagram.instagram_handle(), '@safeguard_on')
        for value in ['bad/name', 'bad\nhandle', '', 'a' * 31, None]:
            if value is None:
                continue
            with self.subTest(value=value), self.assertRaises(ValueError):
                instagram.instagram_handle(value)


if __name__ == '__main__':
    unittest.main()

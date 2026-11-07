import base64
from datetime import datetime, timezone
import json
import os
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import wave

import bot
import instagram
import publish_instagram as publisher
import reel_audio
from social_config import load_env


class SocialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {'INSTAGRAM_HANDLE': 'safeguard_on'})
        self.env.start()
        self.metadata = {'account': '@safeguard_on', 'source': {'url': 'https://example.com/news'}}
        self.db = publisher.open_state(self.root / 'instagram.sqlite3')
        self.client = Mock(user='123')

    def tearDown(self):
        self.db.close()
        self.env.stop()
        self.tmp.cleanup()

    def test_publish_once_and_deduplicate(self):
        self.client.call.side_effect = [{'id': '456'}, {'status_code': 'FINISHED'}, {'id': '789'}]
        self.assertEqual(publisher.publish(self.db, self.client, self.metadata, 'Caption', 'https://example.com/final.mp4'), 'published')
        self.assertEqual(publisher.publish(self.db, self.client, self.metadata, 'Caption', 'https://example.com/final.mp4'), 'published')
        self.assertEqual(self.client.call.call_count, 3)
        self.assertEqual(self.db.execute('SELECT media FROM instagram_publications').fetchone()[0], '789')

    def test_processing_can_resume_without_recreating_container(self):
        self.client.call.side_effect = [{'id': '456'}, {'status_code': 'IN_PROGRESS'},
                                        {'status_code': 'FINISHED'}, {'id': '789'}]
        self.assertEqual(publisher.publish(self.db, self.client, self.metadata, 'Caption', 'https://example.com/final.mp4'), 'processing')
        self.assertEqual(publisher.resume(self.db, self.client, self.metadata['source']['url']), 'published')
        self.assertEqual(sum(c.args[0].endswith('/media') for c in self.client.call.call_args_list), 1)

    def test_uncertain_publish_cannot_send_twice(self):
        self.client.call.side_effect = [{'id': '456'}, {'status_code': 'FINISHED'}, RuntimeError('Timeout')]
        with self.assertRaises(RuntimeError):
            publisher.publish(self.db, self.client, self.metadata, 'Caption', 'https://example.com/final.mp4')
        self.assertEqual(publisher.resume(self.db, self.client, self.metadata['source']['url']), 'publishing')
        self.assertEqual(self.client.call.call_count, 3)

    def test_uncertain_container_creation_is_not_retried(self):
        self.client.call.side_effect = RuntimeError('Timeout')
        with self.assertRaises(RuntimeError):
            publisher.publish(self.db, self.client, self.metadata, 'Caption', 'https://example.com/final.mp4')
        self.assertEqual(publisher.publish(self.db, self.client, self.metadata, 'Caption', 'https://example.com/final.mp4'), 'creating')
        self.assertEqual(self.client.call.call_count, 1)

    def test_daily_limit_counts_pending_attempts(self):
        import time
        for i in range(15):
            self.db.execute('INSERT INTO instagram_publications VALUES (?,?,?,?,?,?)',
                            ('@safeguard_on', str(i), 'publishing', None, None, time.time()))
        self.db.commit()
        with self.assertRaises(RuntimeError):
            publisher.publish(self.db, self.client, self.metadata, 'Caption', 'https://example.com/final.mp4')
        self.client.call.assert_not_called()

    def test_mismatched_account_stops_before_claim(self):
        self.client.check_account.side_effect = ValueError('Wrong account')
        with self.assertRaises(ValueError):
            publisher.publish(self.db, self.client, self.metadata, 'Caption', 'https://example.com/final.mp4')
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM instagram_publications').fetchone()[0], 0)

    def test_publisher_rejects_demo_and_modified_final_files(self):
        import hashlib
        examples = Path(instagram.__file__).with_name('examples')
        article = instagram.load_article(examples / 'instagram-source.json')
        pack = json.loads((examples / 'instagram-pack.json').read_text(encoding='utf-8'))
        root = instagram.save_pack(self.root, article, pack, demo=True)
        video = root / 'final.mp4'
        video.write_bytes(b'test video')
        with self.assertRaises(ValueError):
            publisher.load_publication(root, video)
        data = json.loads((root / 'pack.json').read_text(encoding='utf-8'))
        data['demo'] = False
        (root / 'pack.json').write_text(json.dumps(data), encoding='utf-8')
        manifest = {'final': True, **{key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in [
            ('video_sha256', video), ('pack_sha256', root / 'pack.json'), ('caption_sha256', root / 'caption.txt')]}}
        video.with_suffix('.mp4.manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        self.assertEqual(publisher.load_publication(root, video)[0]['account'], '@safeguard_on')
        (root / 'caption.txt').write_text('Changed after render', encoding='utf-8')
        with self.assertRaises(ValueError):
            publisher.load_publication(root, video)

    def test_local_media_urls_rejected(self):
        for url in ['http://example.com/v.mp4', 'https://localhost/v.mp4', 'https://127.0.0.1/v.mp4',
                    'https://10.0.0.1/v.mp4', 'https://[::1]/v.mp4', 'https://user:secret@example.com/v.mp4']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                publisher.public_video_url(url)

    def test_tts_pcm_to_valid_wav_and_rejects_truncated_audio(self):
        response = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'inlineData': {
            'mimeType': 'audio/L16;codec=pcm;rate=24000', 'data': base64.b64encode(b'\x00\x00' * 24000).decode()}}]}}]}
        output = self.root / 'voice.wav'
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-only'}), \
                patch('reel_audio.request', return_value=json.dumps(response).encode()) as req:
            reel_audio.generate_scene('Salom', output)
            with wave.open(str(output)) as wav:
                self.assertEqual(wav.getnframes(), 24000)
                self.assertEqual(wav.getframerate(), 24000)
            response['candidates'][0]['finishReason'] = 'MAX_TOKENS'
            req.return_value = json.dumps(response).encode()
            with self.assertRaises(RuntimeError):
                reel_audio.generate_scene('Salom', self.root / 'bad.wav')
            self.assertFalse((self.root / 'bad.wav').exists())

    def test_original_music_length_nonzero_and_preserves_output(self):
        output = self.root / 'music.wav'
        reel_audio.synthesize_music(output, 1)
        with wave.open(str(output)) as wav:
            self.assertEqual(wav.getnframes(), 24000)
            self.assertNotEqual(set(wav.readframes(24000)), {0})
        with self.assertRaises(FileExistsError):
            reel_audio.synthesize_music(output, 1)

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg is optional in the Telegram image')
    def test_narration_timing_and_paid_scene_cache(self):
        examples = Path(instagram.__file__).with_name('examples')
        pack = json.loads((examples / 'instagram-pack.json').read_text(encoding='utf-8'))
        article = instagram.load_article(examples / 'instagram-source.json')
        root = instagram.save_pack(self.root, article, pack, demo=True)
        durations = {scene['voiceover']: scene['duration'] for scene in pack['scenes']}
        def generated(text, destination):
            reel_audio.write_wav(destination, b'\x01\x00' * int(durations[text] * 0.8 * 24000))
        with patch('reel_audio.generate_scene', side_effect=generated) as tts:
            result = reel_audio.narrate(root)
            self.assertEqual(tts.call_count, 5)
        with wave.open(str(result)) as wav:
            self.assertEqual(wav.getnframes(), 26 * 24000)
        result.unlink()
        with patch('reel_audio.generate_scene') as tts:
            reel_audio.narrate(root)
            tts.assert_not_called()

    def test_explicit_env_preserves_inherited_credentials(self):
        config = self.root / 'social.env'
        config.write_text('GEMINI_API_KEY=from-file\nINSTAGRAM_USER_ID=123\n', encoding='utf-8')
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'inherited'}):
            load_env(config)
            self.assertEqual(os.environ['GEMINI_API_KEY'], 'inherited')
            self.assertEqual(os.environ['INSTAGRAM_USER_ID'], '123')


if __name__ == '__main__':
    unittest.main()

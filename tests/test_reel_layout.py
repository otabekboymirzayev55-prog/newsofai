import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from reel_layout import cue_srt, load_assets, subtitle_cues


class LayoutTests(unittest.TestCase):
    def test_subtitles_cover_each_scene_without_overlap(self):
        scenes = [{'duration': 2, 'voiceover': 'Bir ikki uch to‘rt'},
                  {'duration': 6, 'voiceover': 'Besh olti yetti sakkiz to‘qqiz o‘n o‘n_bir'}]
        cues = subtitle_cues(scenes)
        self.assertEqual(cues[0]['start'], 0)
        self.assertEqual(cues[-1]['end'], 8)
        self.assertEqual(' '.join(c['text'] for c in cues), ' '.join(s['voiceover'] for s in scenes))
        self.assertTrue(all(len(c['text'].split()) <= 4 for c in cues))
        self.assertTrue(all(a['end'] == b['start'] for a, b in zip(cues, cues[1:])))
        self.assertIn('00:00:00,000 --> 00:00:02,000', cue_srt(cues))
        self.assertIn('--> 00:00:08,000', cue_srt(cues))

    def test_assets_reject_escape_remote_paths_and_missing_rights(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'clip.mp4').write_bytes(b'test')
            manifest = root / 'assets.json'
            for item in [{'path': '../clip.mp4', 'rights': 'owned', 'credit': 'Test'},
                         {'path': 'https://example.com/clip.mp4', 'rights': 'owned', 'credit': 'Test'},
                         {'path': 'clip.mp4', 'credit': 'Test'}]:
                manifest.write_text(json.dumps([item]), encoding='utf-8')
                with self.subTest(item=item), self.assertRaises(ValueError):
                    load_assets(manifest, 1)
            manifest.write_text(json.dumps([{'path': 'clip.mp4', 'rights': 'owned', 'credit': 'Own demo'}]))
            self.assertEqual(load_assets(manifest, 1)[0]['path'], root / 'clip.mp4')

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'Optional FFmpeg integration')
    def test_real_clips_at_correct_times_with_voice_and_music(self):
        from instagram import load_article, save_pack
        from reel_audio import synthesize_music
        from render_reel import render
        examples = Path(__file__).resolve().parents[1] / 'examples'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = save_pack(root, load_article(examples / 'instagram-source.json'),
                             json.loads((examples / 'instagram-pack.json').read_text(encoding='utf-8')), True)
            for name, color in [('red', 'red'), ('blue', 'blue')]:
                subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi',
                                '-i', f'color=c={color}:s=320x240:d=1:r=24', '-c:v', 'libx264',
                                str(pack / f'{name}.mp4')], check=True)
            assets = [None] * 5
            for i, name in [(0, 'red'), (2, 'blue')]:
                assets[i] = {'path': f'{name}.mp4', 'rights': 'owned', 'credit': 'TEST fixture'}
            (pack / 'assets.json').write_text(json.dumps(assets))
            audio = synthesize_music(pack / 'test.wav', 1)
            output = render(pack, pack / 'preview.mp4', voice=audio, music=audio)
            for timestamp, expected in [('0.5', 0), ('9', 2)]:
                pixel = subprocess.check_output(['ffmpeg', '-hide_banner', '-loglevel', 'error',
                                                 '-ss', timestamp, '-i', str(output), '-frames:v', '1',
                                                 '-vf', 'crop=2:2:540:800', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
                self.assertGreater(pixel[expected], 170)
                self.assertLess(pixel[2 if expected == 0 else 0], 60)
            streams = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                                          '-of', 'json', str(output)]))['streams']
            self.assertEqual([s['codec_type'] for s in streams], ['video', 'audio'])

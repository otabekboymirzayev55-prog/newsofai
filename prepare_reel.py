"""One-command editorial pack → narration → music → vertical MP4. Never publishes."""
import argparse
import json
from pathlib import Path
import subprocess
import wave

from bot import article_id
from instagram import fresh_articles, generate_pack, load_article, save_pack
from reel_audio import narrate, synthesize_music
from render_reel import render
from social_config import load_env


def prepare(root, pack_dir=None, demo=False, final=False, music_style='calm'):
    if demo and final:
        raise ValueError('A demo cannot be a final publication')
    if pack_dir:
        target = Path(pack_dir)
    elif demo:
        examples = Path(__file__).with_name('examples')
        article = load_article(examples / 'instagram-source.json')
        target = Path(root) / ('demo-' + article_id(article)[:24])
        if not target.exists():
            save_pack(root, article, json.loads((examples / 'instagram-pack.json').read_text(encoding='utf-8')), True)
    else:
        article = next((a for a in fresh_articles() if not (Path(root) / article_id(a)[:24]).exists()), None)
        if article is None:
            raise RuntimeError('No fresh unprepared source. Use --pack-dir to resume an existing pack')
        target = save_pack(root, article, generate_pack(article))
    data = json.loads((target / 'pack.json').read_text(encoding='utf-8'))
    from instagram import validate_pack
    pack = validate_pack(data)
    if final and data.get('demo'):
        raise ValueError('Demo content cannot be published')
    voice = target / 'narration.wav'
    if not data.get('demo') and not voice.exists():
        narrate(target)
    music = target / 'music.wav'
    if not music.exists():
        synthesize_music(music, sum(s['duration'] for s in pack['scenes']), music_style)
    output = target / ('final.mp4' if final else 'preview.mp4')
    render(target, output, voice=voice if voice.exists() else None, music=music, final=final)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', help='Explicit private social.env, never printed')
    parser.add_argument('--out', default='.local/reels')
    parser.add_argument('--pack-dir', help='Resume a pack without fetching/generating more news')
    parser.add_argument('--demo', action='store_true', help='Offline preview with original music, no AI narration')
    parser.add_argument('--final', action='store_true', help='Render real, checked material for publication')
    parser.add_argument('--music-style', choices=['calm', 'upbeat'], default='calm')
    args = parser.parse_args()
    if args.demo and args.pack_dir:
        parser.error('--demo and --pack-dir cannot be combined')
    try:
        load_env(args.env_file)
        video = prepare(args.out, args.pack_dir, args.demo, args.final, args.music_style)
        print(f'Video ready: {video}')
        print('Inspect facts, audio pronunciation and scene timing before publication. Nothing uploaded.')
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError, wave.Error):
        print('Preparation stopped. Existing packs/audio preserved. Check configuration and resume with --pack-dir.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

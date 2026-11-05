"""Render a vertical review video with local FFmpeg; no uploads or remote media."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap

from instagram import instagram_handle, validate_pack


def render(pack_dir, output, voice=None, music=None, font=None, final=False):
    pack_dir, output = Path(pack_dir).resolve(), Path(output).resolve()
    metadata = json.loads((pack_dir / 'pack.json').read_text(encoding='utf-8'))
    pack = validate_pack(metadata)
    if final and (metadata.get('demo') or not voice):
        raise ValueError('Final video requires a real source and narration')
    if output.exists():
        raise ValueError('Output exists; choose a new path')
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('Install FFmpeg to render the review video')
    fonts = [Path(font)] if font else [
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'),
        Path('C:/Windows/Fonts/arial.ttf'),
    ]
    selected = next((p for p in fonts if p.is_file()), None)
    if selected is None:
        raise ValueError('Pass --font with a local Unicode TrueType font')
    duration = sum(s['duration'] for s in pack['scenes'])
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='newsofai-reel-') as tmp:
        work = Path(tmp)
        shutil.copyfile(selected, work / 'font.ttf')
        label = ('AI VA TEXNOLOGIYA' if final else
                 ('DEMO / QORALAMA' if metadata.get('demo') else 'QORALAMA / KO‘RIB CHIQISH UCHUN'))
        (work / 'label.txt').write_text(label, encoding='utf-8')
        filters = ['drawbox=x=80:y=280:w=920:h=8:color=0x40dfba:t=fill',
                   "drawtext=fontfile=font.ttf:textfile=label.txt:expansion=none:fontsize=30:fontcolor=0x40dfba:x=80:y=210"]
        if 'account' in metadata:
            (work / 'account.txt').write_text(instagram_handle(metadata['account']), encoding='utf-8')
            filters.append('drawtext=fontfile=font.ttf:textfile=account.txt:expansion=none:'
                           'fontsize=36:fontcolor=0x40dfba:x=80:y=1550')
        start = 0
        for i, scene in enumerate(pack['scenes']):
            end = start + scene['duration']
            for kind, width, size, y, color in [('screen', 26, 62, 400, 'white'),
                                              ('voiceover', 38, 40, 1020, '0xc7d3e6')]:
                filename = f'{kind}{i}.txt'
                (work / filename).write_text(textwrap.fill(scene[kind], width=width), encoding='utf-8')
                filters.append(f"drawtext=fontfile=font.ttf:textfile={filename}:expansion=none:fontsize={size}:"
                               f"fontcolor={color}:line_spacing=18:x=80:y={y}:enable='gte(t,{start})*lt(t,{end})'")
            start = end
        cmd = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-n', '-f', 'lavfi', '-i',
               f'color=c=0x101a30:s=1080x1920:r=24:d={duration}']
        audio = []
        if voice:
            cmd.extend(['-i', str(Path(voice).resolve())])
            audio.append('[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,apad[voice]')
        if music:
            cmd.extend(['-stream_loop', '-1', '-i', str(Path(music).resolve())])
            audio.append(f'[{2 if voice else 1}:a]volume=0.10[music]')
        cmd.extend(['-vf', ','.join(filters), '-map', '0:v:0'])
        if audio:
            if voice and music:
                audio.append('[voice][music]amix=inputs=2:duration=longest:normalize=0[audio]')
                stream = '[audio]'
            else:
                stream = '[voice]' if voice else '[music]'
            cmd.extend(['-filter_complex', ';'.join(audio), '-map', stream,
                        '-c:a', 'aac', '-ar', '48000', '-b:a', '128k'])
        cmd.extend(['-t', str(duration), '-c:v', 'libx264', '-preset', 'ultrafast',
                    '-crf', '23', '-maxrate', '8M', '-bufsize', '16M',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(work / 'preview.mp4')])
        # Text/audio paths are passed as arguments, never through a shell.
        subprocess.run(cmd, cwd=work, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, timeout=300)
        # Exclusive creation preserves any output created by another process meanwhile.
        with (work / 'preview.mp4').open('rb') as src, output.open('xb') as dst:
            shutil.copyfileobj(src, dst)
    if final:
        manifest = {'final': True, 'video_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                    'pack_sha256': hashlib.sha256((pack_dir / 'pack.json').read_bytes()).hexdigest(),
                    'caption_sha256': hashlib.sha256((pack_dir / 'caption.txt').read_bytes()).hexdigest()}
        output.with_suffix(output.suffix + '.manifest.json').write_text(json.dumps(manifest) + '\n', encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack_dir')
    parser.add_argument('--output', required=True)
    parser.add_argument('--voice', help='Your local Uzbek narration recording')
    parser.add_argument('--music', help='Local instrumental you have rights to use')
    parser.add_argument('--font', help='Local Unicode .ttf font')
    parser.add_argument('--final', action='store_true', help='Publication version of checked real content with narration')
    args = parser.parse_args()
    try:
        result = render(args.pack_dir, args.output, args.voice, args.music, args.font, args.final)
        print(f'Review video ready: {result}')
        if not args.voice:
            print('No narration supplied. Record voiceover.txt before publishing.')
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
        print('Render failed. Check FFmpeg, font, pack and audio files; choose a new output path.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

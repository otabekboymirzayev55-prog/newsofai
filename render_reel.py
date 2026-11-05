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
from reel_layout import cue_srt, load_assets, subtitle_cues


def render(pack_dir, output, voice=None, music=None, font=None, final=False, text_only=False, assets=None):
    pack_dir, output = Path(pack_dir).resolve(), Path(output).resolve()
    metadata = json.loads((pack_dir / 'pack.json').read_text(encoding='utf-8'))
    pack = validate_pack(metadata)
    supplied_assets = assets or (pack_dir / 'assets.json' if (pack_dir / 'assets.json').is_file() else None)
    clips = load_assets(supplied_assets, len(pack['scenes']))
    if final and (metadata.get('demo') or (not voice and not text_only)):
        raise ValueError('Final video requires real content and narration or explicit text-only mode')
    if text_only and voice:
        raise ValueError('Choose narration or text-only mode')
    subtitle_path = output.with_suffix('.srt')
    if output.exists() or subtitle_path.exists():
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
                   'drawbox=x=80:y=560:w=920:h=600:color=0x172842:t=fill',
                   f"drawbox=x=80:y=1640:w=920:h=4:color=0x283b56:t=fill",
                   f"drawtext=fontfile=font.ttf:text='Safeguard On':fontsize=28:fontcolor=0xc7d3e6:x=80:y=1600",
                   "drawtext=fontfile=font.ttf:textfile=label.txt:expansion=none:fontsize=30:fontcolor=0x40dfba:x=80:y=210"]
        if 'account' in metadata:
            (work / 'account.txt').write_text(instagram_handle(metadata['account']), encoding='utf-8')
            filters.append('drawtext=fontfile=font.ttf:textfile=account.txt:expansion=none:'
                           'fontsize=30:fontcolor=0x40dfba:x=80:y=1500')
        # All screen text is loaded from files, so source punctuation cannot become a filter expression.
        start = 0
        clip_windows = []
        for i, scene in enumerate(pack['scenes']):
            end = start + scene['duration']
            for kind, width, size, y, color in [('screen', 27, 58, 330, 'white')]:
                filename = f'{kind}{i}.txt'
                (work / filename).write_text(textwrap.fill(scene[kind], width=width), encoding='utf-8')
                filters.append(f"drawtext=fontfile=font.ttf:textfile={filename}:expansion=none:fontsize={size}:"
                               f"fontcolor={color}:line_spacing=18:x=80:y={y}:enable='gte(t,{start})*lt(t,{end})'")
            filters.append(f"drawtext=fontfile=font.ttf:text='{i+1:02} / {len(pack['scenes']):02}':"
                           f"fontsize=28:fontcolor=0x40dfba:x=850:y=210:enable='gte(t,{start})*lt(t,{end})'")
            filters.append(f"drawbox=x={80+int(920*i/len(pack['scenes']))}:y=1640:"
                           f"w={int(920/len(pack['scenes']))-6}:h=4:color=0x40dfba:t=fill:enable='gte(t,{start})'")
            if i in clips:
                clip_windows.append((i, start, end))
                (work / f'credit{i}.txt').write_text(clips[i]['credit'], encoding='utf-8')
                filters.append(f"drawtext=fontfile=font.ttf:textfile=credit{i}.txt:expansion=none:fontsize=24:"
                               f"fontcolor=0xc7d3e6:x=100:y=1120:box=1:boxcolor=0x101a30@0.85:"
                               f"enable='gte(t,{start})*lt(t,{end})'")
            else:
                # Original geometry is a fallback, not a fabricated product screenshot.
                filters.append(f"drawtext=fontfile=font.ttf:text='{i+1:02}':fontsize=190:fontcolor=0x40dfba:"
                               f"x='140+8*sin(t*2)':y=690:enable='gte(t,{start})*lt(t,{end})'")
                for bar in range(6):
                    filters.append(f"drawbox=x={500+bar*58}:y={690+bar*30}:w=24:h={220-bar*25}:"
                                   f"color=0x40dfba@0.35:t=fill:enable='gte(t,{start})*lt(t,{end})'")
            start = end
        for i, cue in enumerate(subtitle_cues(pack['scenes'])):
            (work / f'cue{i}.txt').write_text(textwrap.fill(cue['text'], width=26), encoding='utf-8')
            filters.append(f"drawtext=fontfile=font.ttf:textfile=cue{i}.txt:expansion=none:fontsize=56:"
                           f"fontcolor=white:line_spacing=14:x=80:y=1250:"
                           f"enable='gte(t,{cue['start']:.6f})*lt(t,{cue['end']:.6f})'")
        cmd = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-n', '-f', 'lavfi', '-i',
               f'color=c=0x101a30:s=1080x1920:r=24:d={duration}']
        video_chain = []
        stage = 'base'
        # Put common background cards before overlays and typography after overlays.
        video_chain.append('[0:v]' + ','.join(filters[:3]) + '[base]')
        for index, (scene_id, start, end) in enumerate(clip_windows, 1):
            cmd.extend(['-stream_loop', '-1', '-i', str(clips[scene_id]['path'])])
            video_chain.append(f'[{index}:v]scale=920:600:force_original_aspect_ratio=decrease,'
                               f'pad=920:600:(ow-iw)/2:(oh-ih)/2:color=0x172842,setsar=1,fps=24,'
                               f'trim=duration={end-start},setpts=PTS-STARTPTS+{start}/TB[clip{index}]')
            video_chain.append(f"[{stage}][clip{index}]overlay=80:560:eof_action=pass:repeatlast=0:"
                               f"enable='gte(t,{start})*lt(t,{end})'[stage{index}]")
            stage = f'stage{index}'
        video_chain.append(f'[{stage}]' + ','.join(filters[3:]) + '[video]')
        next_input = len(clip_windows) + 1
        audio = []
        if voice:
            cmd.extend(['-i', str(Path(voice).resolve())])
            audio.append(f'[{next_input}:a]loudnorm=I=-16:TP=-1.5:LRA=11,apad[voice]')
            next_input += 1
        if music:
            cmd.extend(['-stream_loop', '-1', '-i', str(Path(music).resolve())])
            audio.append(f'[{next_input}:a]volume=0.10[music]')
        audio_stream = None
        if audio:
            if voice and music:
                audio.append('[voice][music]amix=inputs=2:duration=longest:normalize=0[audio]')
                stream = '[audio]'
            else:
                stream = '[voice]' if voice else '[music]'
            audio_stream = stream
        (work / 'filters.txt').write_text(';'.join(video_chain + audio), encoding='utf-8')
        cmd.extend(['-filter_complex_script', 'filters.txt', '-map', '[video]'])
        if audio_stream:
            cmd.extend(['-map', audio_stream, '-c:a', 'aac', '-ar', '48000', '-b:a', '128k'])
        cmd.extend(['-t', str(duration), '-c:v', 'libx264', '-preset', 'ultrafast',
                    '-crf', '23', '-maxrate', '8M', '-bufsize', '16M',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(work / 'preview.mp4')])
        # Text/audio paths are passed as arguments, never through a shell.
        subprocess.run(cmd, cwd=work, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE, timeout=300)
        # Exclusive creation preserves any output created by another process meanwhile.
        with (work / 'preview.mp4').open('rb') as src, output.open('xb') as dst:
            shutil.copyfileobj(src, dst)
    with subtitle_path.open('x', encoding='utf-8') as handle:
        handle.write(cue_srt(subtitle_cues(pack['scenes'])))
    if final:
        manifest = {'final': True, 'text_only': text_only, 'video_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
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
    parser.add_argument('--text-only', action='store_true', help='Explicit text-card publication without narration')
    parser.add_argument('--assets', help='JSON list of local demo clips, or null for fallback scenes')
    args = parser.parse_args()
    try:
        result = render(args.pack_dir, args.output, args.voice, args.music, args.font, args.final, args.text_only, args.assets)
        print(f'Review video ready: {result}')
        if not args.voice and not args.text_only:
            print('No narration supplied. Record voiceover.txt before publishing.')
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
        print('Render failed. Check FFmpeg, font, pack and audio files; choose a new output path.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Gemini scene narration and locally synthesized instrumental beds for Reels."""
import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import wave

from bot import request
from instagram import validate_pack


def write_wav(path, pcm, rate=24000):
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm)


def generate_scene(text, destination):
    key = os.environ.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_TTS_MODEL', 'gemini-2.5-flash-preview-tts')
    voice = os.environ.get('GEMINI_TTS_VOICE', 'Kore')
    if not key:
        raise RuntimeError('GEMINI_API_KEY is required for narration')
    if not re.fullmatch(r'[A-Za-z0-9.-]+', model) or not re.fullmatch(r'[A-Za-z]+', voice):
        raise ValueError('Invalid TTS model or voice')
    raw = request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', {
        'contents': [{'parts': [{'text': 'Read only the following transcript in clear natural Uzbek. '
                                 'Use a brisk, friendly explanatory voice. Do not add words.\n' + text}]}],
        'generationConfig': {'responseModalities': ['AUDIO'], 'speechConfig': {
            'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}}},
    }, {'x-goog-api-key': key})
    try:
        candidate = json.loads(raw)['candidates'][0]
        if candidate.get('finishReason') != 'STOP':
            raise ValueError('Incomplete audio')
        inline = next(p['inlineData'] for p in candidate['content']['parts'] if 'inlineData' in p)
        # Gemini generateContent PCM is signed 16-bit, little endian, mono.
        if not re.fullmatch(r'audio/(?:L16|pcm);(?:codec=pcm;)?rate=24000', inline['mimeType']):
            raise ValueError('Unexpected audio format')
        pcm = base64.b64decode(inline['data'], validate=True)
        if not 4800 <= len(pcm) <= 24000 * 2 * 20 or len(pcm) % 2:
            raise ValueError('Invalid audio length')
    except (ValueError, KeyError, TypeError, IndexError, StopIteration):
        raise RuntimeError('TTS returned invalid/incomplete audio; no narration saved') from None
    write_wav(destination, pcm)


def narrate(pack_dir):
    root = Path(pack_dir).resolve()
    pack = validate_pack(json.loads((root / 'pack.json').read_text(encoding='utf-8')))
    target = root / 'narration.wav'
    if target.exists():
        raise FileExistsError('Narration exists; preserve it or choose a new pack')
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('FFmpeg is required')
    cache = root / 'audio-cache'
    cache.mkdir(exist_ok=True)
    frames = []
    for scene in pack['scenes']:
        signature = json.dumps([scene['voiceover'], os.environ.get('GEMINI_TTS_MODEL', 'gemini-2.5-flash-preview-tts'),
                                os.environ.get('GEMINI_TTS_VOICE', 'Kore')])
        source = cache / (hashlib.sha256(signature.encode()).hexdigest() + '.wav')
        if not source.exists():
            # Cache each paid response separately; retrying does not repay for completed scenes.
            with tempfile.TemporaryDirectory(dir=cache) as tmp:
                generated = Path(tmp) / 'speech.wav'
                generate_scene(scene['voiceover'], generated)
                generated.replace(source)
        with wave.open(str(source), 'rb') as wav:
            ratio = (wav.getnframes() / wav.getframerate()) / scene['duration']
        if not 0.5 <= ratio <= 1.35:
            raise RuntimeError('Narration does not fit scene timing; edit script or record local narration')
        # Speed up modestly when necessary; shorter speech is padded rather than slowed down.
        with tempfile.TemporaryDirectory(dir=cache) as tmp:
            fitted = Path(tmp) / 'fitted.wav'
            subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(source),
                            '-af', f"atempo={max(1, ratio):.8f},apad,atrim=duration={scene['duration']}",
                            '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', str(fitted)],
                           check=True, stderr=subprocess.PIPE, timeout=60)
            with wave.open(str(fitted), 'rb') as wav:
                frames.append(wav.readframes(wav.getnframes()))
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        result = Path(tmp) / 'narration.wav'
        write_wav(result, b''.join(frames))
        with result.open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst)
    return target


def synthesize_music(destination, duration, style='calm'):
    """Original procedural pad/pluck bed. No external recordings or track claims."""
    if style not in ('calm', 'upbeat') or not 1 <= duration <= 60:
        raise ValueError('Invalid music settings')
    rate = 24000
    bpm = 84 if style == 'calm' else 108
    # Cmaj7, Am7, Fmaj7, G6. A quiet pad plus a soft off-beat pluck.
    chords = [(130.81, 164.81, 196, 246.94), (110, 130.81, 164.81, 196),
              (87.31, 110, 130.81, 164.81), (98, 123.47, 146.83, 164.81)]
    pcm = bytearray()
    for index in range(round(duration * rate)):
        t = index / rate
        bar = 4 * 60 / bpm
        chord = chords[int(t / bar) % len(chords)]
        phase = (t % bar) / bar
        envelope = min(1, phase * 15, (1 - phase) * 15)
        pad = sum(math.sin(2 * math.pi * f * t) for f in chord) * 0.035 * envelope
        beat = t % (60 / bpm)
        pluck = math.sin(2 * math.pi * chord[2] * 2 * t) * math.exp(-beat * 12) * 0.035
        fade = min(1, t / 1.5, (duration - t) / 2)
        pcm.extend(struct.pack('<h', int((pad + pluck) * fade * 32767)))
    target = Path(destination)
    # Exclusive creation protects user-provided audio.
    with target.open('xb') as handle:
        with wave.open(handle, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack_dir')
    parser.add_argument('--music-only', action='store_true', help='No API calls; synthesize a music bed')
    parser.add_argument('--style', choices=['calm', 'upbeat'], default='calm')
    args = parser.parse_args()
    try:
        root = Path(args.pack_dir)
        pack = validate_pack(json.loads((root / 'pack.json').read_text(encoding='utf-8')))
        if not args.music_only:
            print(f'Narration ready: {narrate(root)}')
        print(f"Music ready: {synthesize_music(root / 'music.wav', sum(s['duration'] for s in pack['scenes']), args.style)}")
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError, wave.Error):
        print('Audio preparation failed. Check key/model, scene timing and existing output files. Completed scene audio is cached.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

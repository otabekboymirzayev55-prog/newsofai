"""Short subtitle cues and validated, operator-supplied local demo footage."""
import json
from pathlib import Path


def subtitle_cues(scenes, words_per_cue=4):
    """Estimate phrase timing within each already aligned narration scene (not ASR)."""
    cues, start = [], 0.0
    for scene in scenes:
        words = scene['voiceover'].split()
        for index in range(0, len(words), words_per_cue):
            chunk = words[index:index + words_per_cue]
            cues.append({'start': start + scene['duration'] * index / len(words),
                         'end': start + scene['duration'] * (index + len(chunk)) / len(words),
                         'text': ' '.join(chunk)})
        start += scene['duration']
    return cues


def load_assets(path, scene_count):
    if not path:
        return {}
    manifest = Path(path).resolve()
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(data, list) or len(data) != scene_count:
        raise ValueError('Assets must contain one entry (or null) per scene')
    assets = {}
    for i, item in enumerate(data):
        if item is None:
            continue
        if not isinstance(item, dict) or item.get('rights') not in ('owned', 'licensed', 'permission'):
            raise ValueError('Declare the footage usage rights')
        credit = item.get('credit', '')
        if not isinstance(credit, str) or not credit.strip() or len(credit) > 100 or any(ord(c) < 32 for c in credit):
            raise ValueError('Provide a short footage credit')
        raw = item.get('path')
        if not isinstance(raw, str) or not raw or '://' in raw:
            raise ValueError('Use a local clip path')
        clip = (manifest.parent / raw).resolve()
        if not clip.is_relative_to(manifest.parent) or not clip.is_file() or clip.suffix.lower() not in ('.mp4', '.mov', '.webm'):
            raise ValueError('Clip must be inside the assets directory and use a supported video format')
        assets[i] = {'path': clip, 'credit': credit.strip()}
    return assets


def cue_srt(cues):
    def stamp(value):
        milliseconds = round(value * 1000)
        seconds, ms = divmod(milliseconds, 1000)
        return f'{seconds // 3600:02}:{seconds // 60 % 60:02}:{seconds % 60:02},{ms:03}'
    return '\n'.join(f"{i}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n{cue['text']}\n"
                     for i, cue in enumerate(cues, 1))

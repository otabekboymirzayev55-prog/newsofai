"""Explicit local secret-file loading; values never go to logs."""
import os
from pathlib import Path

ALLOWED = {'GEMINI_API_KEY', 'GEMINI_MODEL', 'GEMINI_TTS_MODEL', 'GEMINI_TTS_VOICE',
           'INSTAGRAM_HANDLE', 'INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_USER_ID', 'INSTAGRAM_GRAPH_VERSION'}


def load_env(path):
    if not path:
        return
    source = Path(path)
    if source.is_symlink():
        raise ValueError('Secret file must not be a symlink')
    for line in source.read_text(encoding='utf-8-sig').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, separator, value = line.partition('=')
        key = key.strip()
        if not separator or key not in ALLOWED:
            raise ValueError('Invalid social configuration entry')
        if value.strip():
            os.environ.setdefault(key, value.strip())


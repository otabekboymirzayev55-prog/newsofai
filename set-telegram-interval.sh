#!/usr/bin/env bash
# Update the existing install without rebuilding images or touching its database.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then
    echo 'Run with: sudo bash set-telegram-interval.sh' >&2
    exit 1
fi
envfile=${1:-/etc/newsofai/bot.env}
if ! systemctl cat newsofai.service >/dev/null 2>&1; then
    echo 'newsofai.service not found; no changes made.' >&2
    exit 1
fi
python3 - "$envfile" <<'PY'
import os
import re
import sys
import tempfile
from pathlib import Path

p = Path(sys.argv[1]).resolve(strict=True)
if not p.is_file():
    raise SystemExit('Expected the existing bot environment file.')
original = p.read_text()
lines = [line for line in original.splitlines()
         if not re.match(r'^\s*(?:export\s+)?POST_INTERVAL_HOURS\s*=', line)]
lines.append('POST_INTERVAL_HOURS=1.5')
fd, name = tempfile.mkstemp(prefix='.bot-interval-', dir=p.parent)
try:
    with os.fdopen(fd, 'w') as output:
        output.write('\n'.join(lines) + '\n')
        output.flush()
        os.fsync(output.fileno())
    metadata = p.stat()
    os.chown(name, metadata.st_uid, metadata.st_gid)
    os.chmod(name, 0o600)
    os.replace(name, p)
finally:
    if os.path.exists(name):
        os.unlink(name)
print('POST_INTERVAL_HOURS=1.5 saved; secret values were not displayed.')
PY
systemctl restart newsofai.service
systemctl is-active --quiet newsofai.service
echo 'newsofai restarted. Verify the effective interval and next post in service logs.'

#!/usr/bin/env bash
# Apply the reviewed Telegram code to the existing Oracle/Podman Quadlet install.
# Preserve credentials, volumes, posts, and unrelated services. No key prompts.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run as root on the existing VPS.' >&2; exit 1; }
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
unit=/etc/containers/systemd/newsofai.container
[[ -f "$unit" ]] || { echo 'Expected existing Quadlet not found; no changes made.' >&2; exit 1; }
command -v podman >/dev/null
systemctl is-active --quiet newsofai.service || { echo 'Existing service is not active; inspect before upgrade.' >&2; exit 1; }
work_dir=$(mktemp -d /var/tmp/newsofai-upgrade-XXXXXX)
chmod 700 "$work_dir"
cleanup() { rm -rf -- "$work_dir"; }
trap cleanup EXIT
python3 "$repo_dir/vps_quadlet.py" inspect "$unit" "$work_dir/config.json"
source_hash=$(python3 - "$repo_dir" <<'PY'
import hashlib,sys
from pathlib import Path
root=Path(sys.argv[1]);h=hashlib.sha256()
for name in ['Dockerfile','bot.py','news_selection.py','news_pool.py','vps_quadlet.py']:h.update((root/name).read_bytes())
print(h.hexdigest()[:12])
PY
)
image="localhost/newsofai:editorial-$source_hash"
env_path=$(python3 - "$work_dir/config.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1]))['env'])
PY
)
podman build -t "$image" "$repo_dir"
podman run --rm --network none -v "$repo_dir/tests:/tests:ro,Z" "$image" python -m unittest discover -s /tests -v
# Temporary state only. Never dry-run against the live channel database.
podman run --rm --env-file "$env_path" -e STATE_PATH=/tmp/editorial-review.sqlite3 "$image" python bot.py --dry-run >"$work_dir/preview.txt"
python3 - "$work_dir/preview.txt" <<'PY'
import sys
from pathlib import Path
text=Path(sys.argv[1]).read_text()
if '\nManba: https://' not in text:
    raise SystemExit('No source-backed dry-run post produced. Live service remains unchanged.')
print('Source-backed dry-run completed. Preview:')
print(text)
PY
backup_dir=/etc/newsofai/quadlet-backups
install -d -m 700 "$backup_dir"
backup="$backup_dir/newsofai-$(date -u +%Y%m%dT%H%M%SZ)-$source_hash.container"
cp --preserve=mode,ownership,timestamps -- "$unit" "$backup"
chmod 600 "$backup"
rollback() {
    echo 'Upgrade activation failed; restoring the original Quadlet.' >&2
    cp -- "$backup" "$unit"
    systemctl daemon-reload
    systemctl restart newsofai.service
}
trap 'rollback; cleanup' ERR
python3 "$repo_dir/vps_quadlet.py" patch "$unit" "$image"
systemctl daemon-reload
systemctl restart newsofai.service
systemctl is-active --quiet newsofai.service
# Inspect only non-secret runtime properties, never dump container environment.
podman inspect newsofai --format '{{json .Config.Env}}' | python3 -c 'import json,sys; vals=json.load(sys.stdin); assert "POST_INTERVAL_HOURS=1.5" in vals; print("Effective interval: 90 minutes")'
trap - ERR
echo "Activated $image; existing volumes and credentials retained."
echo 'Daily ceiling in this image: 18 posts per Asia/Tashkent day.'
echo "Rollback Quadlet: $backup"
echo 'Service activation is confirmed; first real publication still needs observation.'

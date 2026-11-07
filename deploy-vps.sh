#!/usr/bin/env bash
# Oracle Linux 9 / Podman. Run from the extracted project directory.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then
    echo 'Run with: sudo bash deploy-vps.sh' >&2
    exit 1
fi
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
unit=/etc/containers/systemd/newsofai.container
appdir=/opt/newsofai
if [[ -e "$unit" ]] || systemctl cat newsofai.service >/dev/null 2>&1; then
    echo 'Existing newsofai service found; leaving it unchanged.' >&2
    exit 1
fi
if [[ -e "$appdir" && ! -f "$appdir/.newsofai-installer" ]]; then
    echo '/opt/newsofai already exists; leaving existing files unchanged.' >&2
    exit 1
fi
dnf install -y podman
install -d -m 700 "$appdir" /etc/newsofai
touch "$appdir/.newsofai-installer"
install -m 600 bot.py news_selection.py news_pool.py vps_quadlet.py instagram.py render_reel.py reel_layout.py reel_audio.py prepare_reel.py publish_instagram.py run_social_queue.py social_config.py configure_social.py Dockerfile .dockerignore "$appdir/"
install -d -m 700 "$appdir/examples"
install -m 600 examples/*.json "$appdir/examples/"
podman build -t localhost/newsofai:latest "$appdir"
# Run the functional unit tests in the same image used for the service.
podman run --rm --network none -v "$PWD/tests:/tests:ro,Z" \
    localhost/newsofai:latest python -m unittest discover -s /tests -v
envfile=/etc/newsofai/bot.env
if [[ ! -f "$envfile" ]]; then
    echo 'Kalitlar ekranda ko‘rinmaydi. Har birini kiriting va Enter bosing.'
    read -r -s -p 'Telegram bot token: ' telegram_token </dev/tty
    echo
    read -r -p 'Kanal username (@kanal) yoki raqamli ID: ' channel </dev/tty
    read -r -s -p 'Gemini API key: ' gemini_key </dev/tty
    echo
    if [[ ! "$telegram_token" =~ ^[0-9]+:[A-Za-z0-9_-]+$ || ! "$channel" =~ ^(@[A-Za-z0-9_]+|-[0-9]+)$ || ! "$gemini_key" =~ ^[A-Za-z0-9_-]+$ ]]; then
        echo 'Sozlamalar formati noto‘g‘ri; kalitlar saqlanmadi.' >&2
        exit 1
    fi
    (umask 077; printf 'TELEGRAM_BOT_TOKEN=%s\nTELEGRAM_CHANNEL_ID=%s\nGEMINI_API_KEY=%s\nPOST_INTERVAL_HOURS=1.5\n' \
        "$telegram_token" "$channel" "$gemini_key" > "$envfile")
    unset telegram_token gemini_key
fi
chmod 600 "$envfile"
podman volume create newsofai-data >/dev/null
echo 'Sinov: yangilik olinadi va o‘zbekcha matn yaratiladi, kanalga yuborilmaydi.'
podman run --rm --env-file "$envfile" -v newsofai-data:/data \
    localhost/newsofai:latest python bot.py --dry-run
install -d -m 755 /etc/containers/systemd
cat > "$unit" <<'UNIT'
[Unit]
Description=NewsofAI Telegram channel publisher
Wants=network-online.target
After=network-online.target

[Container]
Image=localhost/newsofai:latest
ContainerName=newsofai
EnvironmentFile=/etc/newsofai/bot.env
Volume=newsofai-data:/data

[Service]
Restart=always
RestartSec=30
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl start newsofai.service
systemctl is-active newsofai.service
echo 'Xizmat ishga tushdi. Kanalda post chiqqanini tekshiring.'
echo 'Loglar: sudo journalctl -u newsofai.service -n 30 --no-pager'

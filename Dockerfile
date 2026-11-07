FROM python:3.12-slim-bookworm
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STATE_PATH=/data/posts.sqlite3
COPY bot.py news_selection.py /app/
COPY instagram.py render_reel.py reel_layout.py reel_audio.py prepare_reel.py publish_instagram.py run_social_queue.py social_config.py configure_social.py /app/
COPY examples /app/examples
RUN mkdir -p /data
VOLUME ["/data"]
CMD ["python", "bot.py"]

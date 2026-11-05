FROM python:3.12-slim-bookworm
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STATE_PATH=/data/posts.sqlite3
COPY bot.py /app/bot.py
RUN mkdir -p /data
VOLUME ["/data"]
CMD ["python", "bot.py"]

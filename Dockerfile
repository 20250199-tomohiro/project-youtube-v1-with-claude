FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# YouTube の署名解読に必要な JavaScript ランタイム (deno)
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno

WORKDIR /app
COPY requirements.txt .
# 毎回最新の yt-dlp (+ yt-dlp-ejs) を入れる
RUN pip install --no-cache-dir -U -r requirements.txt \
    && pip install --no-cache-dir -U --pre "yt-dlp[default]" || true

COPY . .

# Render は PORT 環境変数を渡します
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 4 --timeout 600

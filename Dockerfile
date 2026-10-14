FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -U -r requirements.txt

COPY . .

# Render は PORT 環境変数を渡します
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 4 --timeout 600

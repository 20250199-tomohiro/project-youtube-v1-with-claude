import os
import shutil
import tempfile

from flask import Flask, jsonify, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 任意: 環境変数 YTDLP_COOKIES に cookies.txt の中身を入れると、
# ログイン必須/ボット判定されるサイトで使えます。
COOKIES_TEXT = os.environ.get("YTDLP_COOKIES")
COOKIES_PATH = None
if COOKIES_TEXT:
    COOKIES_PATH = os.path.join(tempfile.gettempdir(), "cookies.txt")
    with open(COOKIES_PATH, "w", encoding="utf-8") as f:
        f.write(COOKIES_TEXT)


def base_opts():
    opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
    if COOKIES_PATH:
        opts["cookiefile"] = COOKIES_PATH
    return opts


def valid_url(url: str) -> bool:
    return isinstance(url, str) and url.startswith(("http://", "https://"))


@app.route("/")
def index():
    return send_file(os.path.join(BASE_DIR, "index.html"))


@app.route("/api/info", methods=["POST"])
def info():
    url = (request.get_json(silent=True) or {}).get("url", "").strip()
    if not valid_url(url):
        return jsonify(error="有効なURLを入力してください"), 400
    try:
        with yt_dlp.YoutubeDL(base_opts()) as ydl:
            data = ydl.extract_info(url, download=False)
        return jsonify(
            title=data.get("title"),
            thumbnail=data.get("thumbnail"),
            uploader=data.get("uploader"),
            duration=data.get("duration"),
        )
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.route("/api/download")
def download():
    url = request.args.get("url", "").strip()
    kind = request.args.get("kind", "video")  # video | audio
    if not valid_url(url):
        return jsonify(error="有効なURLを入力してください"), 400

    tmpdir = tempfile.mkdtemp(prefix="ytdlp_")

    @after_this_request
    def cleanup(response):
        shutil.rmtree(tmpdir, ignore_errors=True)
        return response

    opts = base_opts()
    opts["outtmpl"] = os.path.join(tmpdir, "%(title).100s.%(ext)s")

    if kind == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        ]
    else:
        opts["format"] = "bv*[height<=720]+ba/b[height<=720]/b"
        opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)
        files = os.listdir(tmpdir)
        if not files:
            raise RuntimeError("ダウンロードに失敗しました")
        path = os.path.join(tmpdir, files[0])
        return send_file(path, as_attachment=True, download_name=files[0])
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify(error=str(e)), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

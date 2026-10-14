# yt-dlp Web (Render)

中央にURL入力欄があるシンプルなダウンロード用Webページです。

## ファイル構成
- `app.py` … Flask + yt-dlp のバックエンド
- `index.html` … フロント(URL入力枠)
- `requirements.txt` / `Dockerfile` … ffmpeg入りのDocker環境
- `render.yaml` … Render用の設定

## デプロイ手順
1. これらのファイルをGitHubリポジトリにpush
2. Render ダッシュボード → **New +** → **Web Service**(または Blueprint で `render.yaml` を使用)
3. リポジトリを選択、Runtime は **Docker** を選ぶ
4. Deploy。完了すると `https://xxxx.onrender.com` で使えます

## ローカルで試す
```
pip install -r requirements.txt   # ffmpegも別途必要
python app.py                      # http://localhost:10000
```

## 注意
- YouTubeなどはRenderのようなクラウドIPを「ボット」と判定してブロックすることがあります。
  その場合は自分のブラウザからエクスポートした `cookies.txt` の中身を環境変数 `YTDLP_COOKIES` に設定してください(それでも不安定なことがあります)。
- 無料プランはメモリ512MB・一定時間アイドルでスリープします。長い/高画質の動画は失敗しやすいので、画質は720pまでに制限しています(`app.py` の `format` で変更可)。
- yt-dlpはサイト側の変更で動かなくなることがあります。その場合は再デプロイ(Clear build cache)で最新版になります。
- 自分が権利を持つ動画、またはダウンロードが許可されている動画にのみ使ってください。公開サービスとして他人に開放するのは各サイトの利用規約に抵触する可能性があります。URL入力欄は誰でも使えるので、公開する場合はBasic認証などでアクセス制限をかけるのをおすすめします。

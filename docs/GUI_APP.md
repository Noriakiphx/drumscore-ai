# DrumScore AI GUI App

## 目的
Score JSON v1.0を中心に、ドラム譜の表示・編集・変換API呼び出しを行うWeb GUIです。

## 実装済み
- Next.js / React フロントエンド
- Score JSON v1.0 読み込み・直接編集
- 小節番号、セクション、コード、ドラムイベント表示
- ゴーストノート表示
- 音符クリック編集
- 音符追加 / 削除
- Validate API呼び出し
- Score JSON → MIDI出力
- Score JSON → MusicXML出力
- 音源アップロード → Job作成 → Score取得の導線

## 起動
Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

ブラウザで http://localhost:3000 を開きます。

## API接続先
デフォルトは `http://localhost:8000` です。変更する場合:

```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

## 次の実装候補
- VexFlow / OpenSheetMusicDisplayによる正式五線譜レンダリング
- WebAudio / SoundFontによるブラウザ内ドラム再生
- MIDIインポート画面
- MusicXMLインポート
- WAVレンダリングAPI
- ドラッグ&ドロップによる音符移動
- 小節単位の再量子化

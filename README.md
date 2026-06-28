# DrumScore AI - Demucs API Architecture

Moisesに依存せず、Demucsを内蔵したサーバー側APIとして組み直したMVPスターターです。

## 方針

- Source Separationは差し替え可能なEngine設計
- 初期EngineはDemucs
- APIは非同期Job方式
- 分離結果 `drums.wav` を後段のドラム採譜パイプラインに渡す
- BPMは平均値だけでなくテンポマップとして保持
- スコア内部表現はJSON、出力はMusicXML/PDF/MIDIへ拡張

## Pipeline

```text
Audio Upload
  -> Job Create
  -> Separation Engine
      -> Demucs / Mock / Future Model
  -> drums.wav
  -> Drum Event Detector
  -> Tempo Map
  -> Chord/Section Analyzer
  -> Score JSON
  -> MusicXML / PDF / MIDI
```

## First MVP API

- `POST /v1/jobs` 音源アップロード
- `GET /v1/jobs/{job_id}` 進捗確認
- `GET /v1/jobs/{job_id}/stems/drums` drums.wav取得
- `GET /v1/jobs/{job_id}/score` スコアJSON取得

## Engine切替

`.env` または環境変数で指定します。

```bash
SEPARATION_ENGINE=demucs
# or
SEPARATION_ENGINE=mock
```

開発初期は `mock`、GPUサーバーでは `demucs` を使います。


## Score JSON v1.0 + Conversion API

追加済み:

- `schemas/score-json-v1.schema.json`
- `docs/SCORE_JSON_V1.md`
- `docs/CONVERSION_API.md`
- `POST /v1/validate/score`
- `POST /v1/convert/score-to-midi`
- `POST /v1/convert/midi-to-score`
- `POST /v1/convert/score-to-musicxml`

内部正本は `Score JSON v1.0` に固定します。

## GUI App

`frontend/` にNext.jsベースのGUIを追加しました。

- Score JSON v1.0の表示・編集
- 小節番号 / セクション / コード / ドラムイベント表示
- ゴーストノート編集
- MIDI / MusicXML出力API連携
- Audio Upload → Job → Score取得

詳細は `docs/GUI_APP.md` を参照してください。

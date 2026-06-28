# Score JSON v1.0

DrumScore AI の内部正本フォーマットです。すべての変換はこの JSON を中心に行います。

```text
Audio ⇄ MIDI ⇄ Score JSON ⇄ MusicXML ⇄ PDF/PNG
                     ⇅
                    WAV
```

## 必須トップレベル

- `metadata`: 曲名、アーティスト、schema version
- `average_bpm`: 曲全体の平均BPM
- `time_signature`: 拍子
- `ticks_per_quarter`: MIDI/グリッド変換用のTPQ
- `tempo_map`: 可変BPMの拍アンカー
- `sections`: Intro / Verse / Chorus など
- `bars`: 小節境界
- `chords`: 小節/拍に紐づくコード
- `drum_events`: ドラムイベント

## ゴーストノート

ゴーストノートは以下の両方で表現します。

```json
{
  "instrument": "snare_ghost",
  "velocity": 35,
  "articulation": "ghost"
}
```

MusicXML出力時は括弧付きノートヘッド、MIDI出力時は低ベロシティで出力します。

## 可変BPM

`tempo_map` は拍ごとのテンポ追従に使います。

```json
{
  "time_sec": 12.304,
  "beat_index": 16,
  "bpm": 81.7,
  "confidence": 0.92
}
```

MVPのMIDI出力は平均BPMを使います。次フェーズで tempo_map を MIDI tempo changes として書き出します。

## スキーマファイル

`schemas/score-json-v1.schema.json`

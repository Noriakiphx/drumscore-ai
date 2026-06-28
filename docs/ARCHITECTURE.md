# Architecture

## Key Change

Moises APIを直接呼ぶ設計から、サーバー内でSource Separationを実行する設計に変更。

## SeparationEngine Interface

```python
class SeparationEngine:
    def separate(input_audio: Path, output_dir: Path) -> SeparationResult:
        ...
```

## Engines

- MockSeparationEngine: 開発用。入力をdrums.wavとしてコピー。
- DemucsSeparationEngine: 本番候補。Demucs CLIをサーバー上で実行。
- Future: MDX-Net / UVR models / proprietary drum part model.

## Important Product Rule

BPMは固定値ではなく、平均BPM + beat-level tempo mapとして扱う。
譜面の小節境界と16分グリッドはテンポマップに追従する。

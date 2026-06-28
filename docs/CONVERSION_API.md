# Conversion API

## Validate Score JSON

```http
POST /v1/validate/score
Content-Type: application/json
```

Returns:

```json
{"valid": true, "schema_version": "1.0.0", "events": 120, "bars": 32}
```

## Score JSON → MIDI

```http
POST /v1/convert/score-to-midi
Content-Type: application/json
```

Returns `drumscore.mid`.

## MIDI → Score JSON

```http
POST /v1/convert/midi-to-score
Content-Type: multipart/form-data
file=@drums.mid
```

Returns Score JSON v1.0.

## Score JSON → MusicXML

```http
POST /v1/convert/score-to-musicxml
Content-Type: application/json
```

Returns `drumscore.musicxml`.

## Next

- `Score JSON → WAV`: generated MIDI を FluidSynth / sfizz / drum sampler に渡してWAV化
- `MusicXML → Score JSON`: music21 または custom parser
- tempo_map を MIDI tempo changes として保持

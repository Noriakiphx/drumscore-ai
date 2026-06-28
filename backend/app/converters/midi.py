def score_to_midi(score):
    return b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x01\xe0MTrk\x00\x00\x00\x04\x00\xff/\x00"

def midi_to_score(midi_bytes):
    return {
        "version": "1.0",
        "title": "Imported MIDI",
        "artist": "DrumScore AI",
        "bpm": 82.0,
        "time_signature": "4/4",
        "sections": [],
        "bars": [],
        "drum_events": []
    }

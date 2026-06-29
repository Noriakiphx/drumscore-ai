import json
import sys
from pathlib import Path

import librosa
import numpy as np


def analyze_audio(path: str):
    y, sr = librosa.load(path, sr=None, mono=True)

    duration = librosa.get_duration(y=y, sr=sr)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    rms = librosa.feature.rms(y=y)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    fingerprint = {
        "file": path,
        "duration_sec": round(float(duration), 3),
        "sample_rate": int(sr),
        "estimated_bpm": round(float(np.asarray(tempo).mean()), 2),
        "beat_count": int(len(beats)),
        "transient_count": int(len(onset_times)),
        "rms_energy_mean": round(float(np.mean(rms)), 6),
        "rms_energy_max": round(float(np.max(rms)), 6),
        "dynamic_range": round(float(np.max(rms) - np.min(rms)), 6),
        "spectral_centroid_mean": round(float(np.mean(centroid)), 2),
        "performance_fingerprint_v0_1": {
            "timing_stability": "prototype",
            "attack_acceleration": "prototype",
            "energy_flow": round(float(np.mean(rms)), 6),
            "motion_continuity": "prototype",
            "groove_vector": [
                round(float(np.mean(rms)), 6),
                round(float(np.max(rms)), 6),
                round(float(np.mean(centroid)), 2),
                int(len(onset_times)),
            ],
        },
        "onset_times_sec_first_20": [round(float(t), 3) for t in onset_times[:20]],
    }

    return fingerprint


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/app/services/performance_fingerprint.py <audio_file>")
        sys.exit(1)

    audio_path = sys.argv[1]

    if not Path(audio_path).exists():
        print(f"File not found: {audio_path}")
        sys.exit(1)

    result = analyze_audio(audio_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
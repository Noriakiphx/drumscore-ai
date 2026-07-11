from pathlib import Path
from typing import Any

import librosa
import numpy as np


def _safe_float(value: Any) -> float:
    array = np.asarray(value, dtype=float)
    return float(array.mean()) if array.size else 0.0


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return values
    maximum = float(np.max(values))
    if maximum <= 0:
        return np.zeros_like(values)
    return values / maximum


def _candidate_score(
    bpm: float,
    onset_envelope: np.ndarray,
    sr: int,
    hop_length: int,
) -> tuple[float, dict[str, float]]:
    _, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_envelope,
        sr=sr,
        hop_length=hop_length,
        bpm=float(bpm),
        trim=False,
    )
    beat_frames = np.asarray(beat_frames, dtype=int)
    beat_frames = beat_frames[beat_frames < len(onset_envelope)]

    if len(beat_frames) < 3:
        return 0.0, {
            "alignment": 0.0,
            "stability": 0.0,
            "strong_beat_ratio": 0.0,
        }

    normalized_onsets = _normalize(onset_envelope)
    beat_strengths = normalized_onsets[beat_frames]
    alignment = float(np.mean(beat_strengths))
    strong_beat_ratio = float(np.mean(beat_strengths >= 0.20))

    beat_times = librosa.frames_to_time(
        beat_frames,
        sr=sr,
        hop_length=hop_length,
    )
    intervals = np.diff(beat_times)

    if intervals.size and float(np.mean(intervals)) > 0:
        coefficient_of_variation = float(np.std(intervals) / np.mean(intervals))
        stability = max(0.0, 1.0 - coefficient_of_variation)
    else:
        stability = 0.0

    center_bpm = 90.0
    distance = abs(np.log2(max(bpm, 1.0) / center_bpm))
    tempo_prior = float(np.exp(-0.5 * (distance / 0.80) ** 2))

    score = (
        0.45 * alignment
        + 0.25 * strong_beat_ratio
        + 0.20 * stability
        + 0.10 * tempo_prior
    )

    return score, {
        "alignment": round(alignment, 6),
        "stability": round(stability, 6),
        "strong_beat_ratio": round(strong_beat_ratio, 6),
    }


def estimate_advanced_tempo(
    y: np.ndarray,
    sr: int,
    min_bpm: float = 45.0,
    max_bpm: float = 190.0,
) -> dict[str, Any]:
    hop_length = 512
    _, percussive = librosa.effects.hpss(y)

    onset_envelope = librosa.onset.onset_strength(
        y=percussive,
        sr=sr,
        hop_length=hop_length,
        aggregate=np.median,
    )

    raw_tempo, _ = librosa.beat.beat_track(
        onset_envelope=onset_envelope,
        sr=sr,
        hop_length=hop_length,
        trim=False,
    )
    raw_bpm = _safe_float(raw_tempo)

    local_tempi = librosa.feature.tempo(
        onset_envelope=onset_envelope,
        sr=sr,
        hop_length=hop_length,
        aggregate=None,
    )
    local_tempi = np.asarray(local_tempi, dtype=float)
    local_tempi = local_tempi[np.isfinite(local_tempi)]

    local_median = float(np.median(local_tempi)) if local_tempi.size else raw_bpm
    source_candidates = [raw_bpm, local_median]
    candidates: set[float] = set()

    for source in source_candidates:
        for ratio in (0.5, 1.0, 2.0):
            candidate = source * ratio
            while candidate < min_bpm:
                candidate *= 2.0
            while candidate > max_bpm:
                candidate /= 2.0
            if min_bpm <= candidate <= max_bpm:
                candidates.add(round(candidate, 3))

    ranked: list[dict[str, Any]] = []
    for candidate in sorted(candidates):
        score, details = _candidate_score(
            candidate,
            onset_envelope,
            sr,
            hop_length,
        )
        ranked.append(
            {
                "bpm": round(candidate, 2),
                "score": round(score, 6),
                **details,
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    selected = ranked[0] if ranked else {"bpm": round(raw_bpm, 2), "score": 0.0}
    second_score = ranked[1]["score"] if len(ranked) > 1 else 0.0
    confidence = max(
        0.0,
        min(1.0, float(selected["score"] - second_score) * 4.0 + 0.5),
    )

    selected_bpm = float(selected["bpm"])
    _, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_envelope,
        sr=sr,
        hop_length=hop_length,
        bpm=selected_bpm,
        trim=False,
    )

    return {
        "estimated_bpm": round(selected_bpm, 2),
        "raw_bpm": round(raw_bpm, 2),
        "confidence": round(confidence, 3),
        "tempo_candidates": ranked,
        "beat_frames": np.asarray(beat_frames, dtype=int),
        "onset_envelope": onset_envelope,
        "hop_length": hop_length,
    }


def build_tempo_map(
    onset_envelope: np.ndarray,
    sr: int,
    hop_length: int,
    selected_bpm: float,
    interval_sec: float = 2.0,
) -> list[dict[str, float]]:
    local_tempi = librosa.feature.tempo(
        onset_envelope=onset_envelope,
        sr=sr,
        hop_length=hop_length,
        aggregate=None,
    )
    local_tempi = np.asarray(local_tempi, dtype=float)

    if local_tempi.size == 0:
        return [{"time_sec": 0.0, "bpm": round(selected_bpm, 2)}]

    frame_times = librosa.frames_to_time(
        np.arange(len(local_tempi)),
        sr=sr,
        hop_length=hop_length,
    )

    def fold_to_reference(value: float) -> float:
        if not np.isfinite(value) or value <= 0:
            return selected_bpm
        adjusted = value
        while adjusted > selected_bpm * 1.5:
            adjusted /= 2.0
        while adjusted < selected_bpm * 0.67:
            adjusted *= 2.0
        return adjusted

    corrected = np.array(
        [fold_to_reference(value) for value in local_tempi],
        dtype=float,
    )

    duration = float(frame_times[-1]) if frame_times.size else 0.0
    points: list[dict[str, float]] = []
    time_sec = 0.0

    while time_sec <= duration:
        mask = (
            (frame_times >= time_sec)
            & (frame_times < time_sec + interval_sec)
        )
        values = corrected[mask]
        bpm = float(np.median(values)) if values.size else selected_bpm
        bpm = float(
            np.clip(
                bpm,
                selected_bpm * 0.75,
                selected_bpm * 1.25,
            )
        )
        points.append(
            {
                "time_sec": round(time_sec, 3),
                "bpm": round(bpm, 2),
            }
        )
        time_sec += interval_sec

    return points


def analyze_audio(path: str) -> dict[str, Any]:
    audio_path = Path(path)

    if not audio_path.exists():
        raise FileNotFoundError(str(audio_path))

    y, sr = librosa.load(str(audio_path), sr=None, mono=True)
    if y.size == 0:
        raise ValueError("Audio file contains no samples")

    duration = librosa.get_duration(y=y, sr=sr)
    tempo_result = estimate_advanced_tempo(y, sr)

    beat_frames = tempo_result["beat_frames"]
    onset_envelope = tempo_result["onset_envelope"]
    hop_length = tempo_result["hop_length"]

    tempo_map = build_tempo_map(
        onset_envelope=onset_envelope,
        sr=sr,
        hop_length=hop_length,
        selected_bpm=tempo_result["estimated_bpm"],
    )

    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_envelope,
        sr=sr,
        hop_length=hop_length,
        backtrack=True,
    )
    onset_times = librosa.frames_to_time(
        onset_frames,
        sr=sr,
        hop_length=hop_length,
    )

    rms = librosa.feature.rms(y=y)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    flux = librosa.onset.onset_strength(y=y, sr=sr)

    rms_mean = _safe_float(rms)
    rms_max = float(np.max(rms)) if rms.size else 0.0
    rms_min = float(np.min(rms)) if rms.size else 0.0
    centroid_mean = _safe_float(centroid)
    zcr_mean = _safe_float(zcr)
    flux_mean = _safe_float(flux)

    return {
        "file": audio_path.name,
        "duration_sec": round(float(duration), 3),
        "sample_rate": int(sr),
        "estimated_bpm": tempo_result["estimated_bpm"],
        "raw_bpm": tempo_result["raw_bpm"],
        "tempo_confidence": tempo_result["confidence"],
        "tempo_candidates": tempo_result["tempo_candidates"],
        "tempo_map": tempo_map,
        "beat_count": int(len(beat_frames)),
        "transient_count": int(len(onset_times)),
        "rms_energy_mean": round(rms_mean, 6),
        "rms_energy_max": round(rms_max, 6),
        "dynamic_range": round(rms_max - rms_min, 6),
        "spectral_centroid_mean": round(centroid_mean, 2),
        "zero_crossing_rate_mean": round(zcr_mean, 6),
        "spectral_flux_mean": round(flux_mean, 6),
        "performance_fingerprint_v0_1": {
            "timing_stability": None,
            "attack_acceleration": None,
            "energy_flow": round(rms_mean, 6),
            "motion_continuity": None,
            "groove_vector": [
                round(rms_mean, 6),
                round(rms_max, 6),
                round(centroid_mean, 2),
                int(len(onset_times)),
                round(zcr_mean, 6),
                round(flux_mean, 6),
            ],
            "status": "prototype",
        },
        "onset_times_sec_first_50": [
            round(float(time), 3)
            for time in onset_times[:50]
        ],
    }

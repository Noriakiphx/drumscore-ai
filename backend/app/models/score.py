from __future__ import annotations

from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


class TimeSignature(BaseModel):
    numerator: int = Field(4, ge=1, le=32)
    denominator: int = Field(4, ge=1)


class TempoPoint(BaseModel):
    """A tempo anchor. beat_index is absolute quarter-note beat index from song start."""
    time_sec: float = Field(..., ge=0)
    beat_index: float = Field(..., ge=0)
    bpm: float = Field(..., gt=20, lt=300)
    confidence: float = Field(1.0, ge=0, le=1)


class Section(BaseModel):
    id: str
    name: str
    start_bar: int = Field(..., ge=1)
    end_bar: int = Field(..., ge=1)

    @model_validator(mode="after")
    def valid_range(self):
        if self.end_bar < self.start_bar:
            raise ValueError("end_bar must be >= start_bar")
        return self


class ChordSymbol(BaseModel):
    bar: int = Field(..., ge=1)
    beat: float = Field(1.0, ge=1)
    symbol: str
    confidence: float = Field(0.5, ge=0, le=1)


class Bar(BaseModel):
    number: int = Field(..., ge=1)
    start_sec: float = Field(..., ge=0)
    end_sec: float = Field(..., ge=0)
    section_id: Optional[str] = None
    rehearsal_mark: Optional[str] = None

    @model_validator(mode="after")
    def valid_range(self):
        if self.end_sec <= self.start_sec:
            raise ValueError("end_sec must be > start_sec")
        return self


class DrumInstrument(str, Enum):
    kick = "kick"
    snare = "snare"
    snare_ghost = "snare_ghost"
    rimshot = "rimshot"
    cross_stick = "cross_stick"
    hihat_closed = "hihat_closed"
    hihat_open = "hihat_open"
    hihat_pedal = "hihat_pedal"
    ride = "ride"
    ride_bell = "ride_bell"
    crash = "crash"
    splash = "splash"
    china = "china"
    tom_high = "tom_high"
    tom_mid = "tom_mid"
    tom_floor = "tom_floor"


class Articulation(str, Enum):
    normal = "normal"
    ghost = "ghost"
    accent = "accent"
    flam = "flam"
    drag = "drag"
    choke = "choke"


class DrumEvent(BaseModel):
    id: Optional[str] = None
    time_sec: float = Field(..., ge=0)
    bar: int = Field(..., ge=1)
    beat: float = Field(..., ge=1, description="1-based beat position inside bar")
    division: int = Field(0, ge=0, description="0-based subdivision index inside beat")
    grid: Literal[4, 8, 12, 16, 24, 32] = 16
    instrument: DrumInstrument
    velocity: int = Field(90, ge=1, le=127)
    articulation: Articulation = Articulation.normal
    duration_sec: float = Field(0.05, ge=0)
    confidence: float = Field(0.5, ge=0, le=1)
    source: Literal["ai", "human", "imported"] = "ai"


class ScoreMetadata(BaseModel):
    title: str = "Untitled"
    artist: Optional[str] = None
    source_audio: Optional[str] = None
    created_by: str = "DrumScore AI"
    schema_version: str = "1.0.0"


class ScoreJSON(BaseModel):
    """Canonical internal representation for DrumScore AI v1.0."""
    model_config = ConfigDict(use_enum_values=True)

    metadata: ScoreMetadata = Field(default_factory=ScoreMetadata)
    average_bpm: float = Field(..., gt=20, lt=300)
    time_signature: TimeSignature = Field(default_factory=TimeSignature)
    ticks_per_quarter: int = Field(480, ge=24)
    tempo_map: list[TempoPoint] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)
    bars: list[Bar] = Field(default_factory=list)
    chords: list[ChordSymbol] = Field(default_factory=list)
    drum_events: list[DrumEvent] = Field(default_factory=list)


# Backward compatible alias used by previous API code.
ScoreDraft = ScoreJSON

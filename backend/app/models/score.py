from typing import Any, Literal
from pydantic import BaseModel, Field
class TempoPoint(BaseModel):
    time_sec: float = Field(ge=0)
    bpm: float = Field(gt=0)
class GuideCue(BaseModel):
    id: str
    time_sec: float = Field(ge=0)
    bar: int = Field(ge=1)
    label: str
    type: Literal["section","count","page_turn","note"] = "section"
    color: str | None = None
class DrumEvent(BaseModel):
    time_sec: float = Field(ge=0)
    bar: int = Field(ge=1)
    beat: float = Field(ge=1)
    instrument: str
    velocity: int = Field(ge=1,le=127)
    motion: dict[str,Any] | None = None
class ScoreJSON(BaseModel):
    version: str = "1.0"
    title: str
    artist: str | None = None
    time_signature: str = "4/4"
    tempo_map: list[TempoPoint]
    guide_cues: list[GuideCue] = []
    drum_events: list[DrumEvent] = []

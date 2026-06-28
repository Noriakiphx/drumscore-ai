from abc import ABC, abstractmethod
from pathlib import Path

class SeparationResult:
    def __init__(self, stems_dir: Path):
        self.stems_dir = stems_dir
        self.drums_path = stems_dir / "drums.wav"
        self.bass_path = stems_dir / "bass.wav"
        self.vocals_path = stems_dir / "vocals.wav"
        self.other_path = stems_dir / "other.wav"

class SeparationEngine(ABC):
    @abstractmethod
    def separate(self, input_audio: Path, output_dir: Path) -> SeparationResult:
        raise NotImplementedError

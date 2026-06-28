from pathlib import Path
import shutil
from .base import SeparationEngine, SeparationResult

class MockSeparationEngine(SeparationEngine):
    """開発用。入力音源を drums.wav としてコピーするだけ。"""
    def separate(self, input_audio: Path, output_dir: Path) -> SeparationResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        drums = output_dir / "drums.wav"
        shutil.copyfile(input_audio, drums)
        return SeparationResult(output_dir)

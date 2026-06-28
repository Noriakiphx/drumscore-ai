from pathlib import Path
import shutil
import subprocess
from .base import SeparationEngine, SeparationResult

class DemucsSeparationEngine(SeparationEngine):
    def __init__(self, model: str = "htdemucs"):
        self.model = model

    def separate(self, input_audio: Path, output_dir: Path) -> SeparationResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        # demucs -n htdemucs --out <output_dir> <audio>
        cmd = [
            "python", "-m", "demucs",
            "-n", self.model,
            "--out", str(output_dir),
            str(input_audio),
        ]
        subprocess.run(cmd, check=True)

        # Demucs output: <out>/<model>/<track_name>/drums.wav
        candidates = list(output_dir.glob(f"{self.model}/*/drums.wav"))
        if not candidates:
            raise FileNotFoundError("Demucs output drums.wav not found")

        normalized_stems_dir = output_dir / "stems"
        normalized_stems_dir.mkdir(exist_ok=True)
        for stem in ["drums", "bass", "vocals", "other"]:
            found = list(output_dir.glob(f"{self.model}/*/{stem}.wav"))
            if found:
                shutil.copyfile(found[0], normalized_stems_dir / f"{stem}.wav")
        return SeparationResult(normalized_stems_dir)

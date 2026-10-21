from pathlib import Path, PureWindowsPath
import json, uuid
from app.core.config import settings
from app.engines.factory import get_separation_engine
from app.services.analyzer import analyze_drums_to_score

class JobStore:
    @staticmethod
    def _validate_filename(filename: str) -> str:
        if (not isinstance(filename, str) or not filename
                or filename in {".", ".."} or "\x00" in filename
                or "/" in filename or "\\" in filename
                or PureWindowsPath(filename).name != filename):
            raise ValueError("Invalid upload filename")
        return filename

    @staticmethod
    def _contained_path(job_dir: Path, path: Path) -> Path:
        resolved = path.resolve()
        if not resolved.is_relative_to(job_dir.resolve()):
            raise ValueError("Job file is outside its storage directory")
        return resolved

    def _job_directory(self, job_id: str) -> Path:
        # Canonicalize IDs before constructing any filesystem path.
        canonical_id = str(uuid.UUID(str(job_id)))
        root = settings.storage_dir.resolve()
        path = root / canonical_id
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Invalid job directory")
        return path

    def create_job(self, filename: str, data: bytes) -> dict:
        filename = self._validate_filename(filename)
        job_id = str(uuid.uuid4())
        job_dir = self._job_directory(job_id)
        job_dir.mkdir(parents=True, exist_ok=False)
        # A user filename must never name job.json, score.json or output files.
        input_filename = "input" + Path(filename).suffix
        input_path = self._contained_path(job_dir, job_dir / input_filename)
        input_path.write_bytes(data)
        meta = {"job_id": job_id, "status": "uploaded", "filename": filename,
                "input_filename": input_filename}
        self._write_meta(job_dir, meta)
        return meta

    def process_job(self, job_id: str) -> dict:
        job_dir = self._job_directory(job_id)
        meta = self._read_meta(job_dir)
        meta["status"] = "separating"
        self._write_meta(job_dir, meta)

        # Keep already-uploaded jobs readable, while validating legacy metadata.
        input_name = self._validate_filename(meta.get("input_filename", meta["filename"]))
        input_path = self._contained_path(job_dir, job_dir / input_name)
        if input_path.is_symlink() or not input_path.is_file():
            raise ValueError("Invalid job input")
        stems_dir = self._contained_path(job_dir, job_dir / "separation")
        result = get_separation_engine().separate(input_path, stems_dir)

        meta["status"] = "analyzing"
        meta["drums_path"] = str(self._contained_path(job_dir, result.drums_path))
        self._write_meta(job_dir, meta)

        score = analyze_drums_to_score(result.drums_path, title=Path(meta["filename"]).stem)
        score_path = self._contained_path(job_dir, job_dir / "score.json")
        score_path.write_text(score.model_dump_json(indent=2), encoding="utf-8")

        meta["status"] = "done"
        meta["score_path"] = str(score_path)
        self._write_meta(job_dir, meta)
        return meta

    def get_job(self, job_id: str) -> dict:
        return self._read_meta(self._job_directory(job_id))

    def get_drums_path(self, job_id: str) -> Path:
        job_dir = self._job_directory(job_id)
        meta = self._read_meta(job_dir)
        path = self._contained_path(job_dir, Path(meta["drums_path"]))
        if not path.is_file():
            raise FileNotFoundError("Drums stem is not available")
        return path

    def get_score(self, job_id: str) -> dict:
        job_dir = self._job_directory(job_id)
        path = self._contained_path(job_dir, job_dir / "score.json")
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_meta(self, job_dir: Path, meta: dict):
        self._contained_path(job_dir, job_dir / "job.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def _read_meta(self, job_dir: Path) -> dict:
        return json.loads(self._contained_path(job_dir, job_dir / "job.json").read_text(encoding="utf-8"))

job_store = JobStore()

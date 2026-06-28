from pathlib import Path
import json, uuid
from app.core.config import settings
from app.engines.factory import get_separation_engine
from app.services.analyzer import analyze_drums_to_score

class JobStore:
    def create_job(self, filename: str, data: bytes) -> dict:
        job_id = str(uuid.uuid4())
        job_dir = settings.storage_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        input_path = job_dir / filename
        input_path.write_bytes(data)
        meta = {"job_id": job_id, "status": "uploaded", "filename": filename}
        self._write_meta(job_dir, meta)
        return meta

    def process_job(self, job_id: str) -> dict:
        job_dir = settings.storage_dir / job_id
        meta = self._read_meta(job_dir)
        meta["status"] = "separating"
        self._write_meta(job_dir, meta)

        input_path = job_dir / meta["filename"]
        stems_dir = job_dir / "separation"
        result = get_separation_engine().separate(input_path, stems_dir)

        meta["status"] = "analyzing"
        meta["drums_path"] = str(result.drums_path)
        self._write_meta(job_dir, meta)

        score = analyze_drums_to_score(result.drums_path, title=Path(meta["filename"]).stem)
        score_path = job_dir / "score.json"
        score_path.write_text(score.model_dump_json(indent=2), encoding="utf-8")

        meta["status"] = "done"
        meta["score_path"] = str(score_path)
        self._write_meta(job_dir, meta)
        return meta

    def get_job(self, job_id: str) -> dict:
        return self._read_meta(settings.storage_dir / job_id)

    def get_score(self, job_id: str) -> dict:
        path = settings.storage_dir / job_id / "score.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_meta(self, job_dir: Path, meta: dict):
        (job_dir / "job.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def _read_meta(self, job_dir: Path) -> dict:
        return json.loads((job_dir / "job.json").read_text(encoding="utf-8"))

job_store = JobStore()

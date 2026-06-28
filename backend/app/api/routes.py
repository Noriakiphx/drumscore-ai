from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse

from app.services.jobs import job_store
from app.models.score import ScoreJSON
from app.converters.midi import score_to_midi, midi_to_score
from app.converters.musicxml import score_to_musicxml

router = APIRouter(prefix="/v1")
EXPORT_DIR = Path("/tmp/drumscore_exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/jobs")
async def create_job(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    data = await file.read()
    job = job_store.create_job(file.filename, data)
    background_tasks.add_task(job_store.process_job, job["job_id"])
    return job

@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    return job_store.get_job(job_id)

@router.get("/jobs/{job_id}/score")
def get_score(job_id: str):
    return job_store.get_score(job_id)

@router.get("/jobs/{job_id}/stems/drums")
def get_drums_stem(job_id: str):
    meta = job_store.get_job(job_id)
    return FileResponse(meta["drums_path"], media_type="audio/wav", filename="drums.wav")

@router.post("/convert/score-to-midi")
def convert_score_to_midi(score: ScoreJSON):
    out = EXPORT_DIR / f"score-{uuid4().hex}.mid"
    score_to_midi(score, out)
    return FileResponse(out, media_type="audio/midi", filename="drumscore.mid")

@router.post("/convert/score-to-musicxml")
def convert_score_to_musicxml(score: ScoreJSON):
    out = EXPORT_DIR / f"score-{uuid4().hex}.musicxml"
    score_to_musicxml(score, out)
    return FileResponse(out, media_type="application/vnd.recordare.musicxml+xml", filename="drumscore.musicxml")

@router.post("/convert/midi-to-score")
async def convert_midi_to_score(file: UploadFile = File(...)):
    midi_path = EXPORT_DIR / f"upload-{uuid4().hex}.mid"
    midi_path.write_bytes(await file.read())
    score = midi_to_score(midi_path, title=file.filename or "Imported MIDI")
    return score.model_dump()

@router.post("/validate/score")
def validate_score(score: ScoreJSON):
    return {"valid": True, "schema_version": score.metadata.schema_version, "events": len(score.drum_events), "bars": len(score.bars)}

from pathlib import Path
from uuid import uuid4
import shutil
from fastapi import APIRouter,File,HTTPException,UploadFile
from app.models.score import GuideCue,ScoreJSON
from app.services.guide_cues import guide_cue_store
from app.services.performance_fingerprint import analyze_audio
router=APIRouter(prefix="/v1")
UPLOAD_DIR=Path("uploads"); UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
@router.post("/performance-fingerprint")
async def performance_fingerprint(file:UploadFile=File(...)):
    stored=UPLOAD_DIR/f"{uuid4().hex}{Path(file.filename or 'upload.bin').suffix}"
    try:
        with stored.open("wb") as b: shutil.copyfileobj(file.file,b)
        r=analyze_audio(str(stored)); r["original_filename"]=file.filename; return r
    except Exception as e: raise HTTPException(status_code=422,detail=str(e)) from e
    finally: stored.unlink(missing_ok=True)
@router.get("/guide-cues",response_model=list[GuideCue])
def list_guide_cues(): return guide_cue_store.list()
@router.post("/guide-cues",response_model=GuideCue)
def add_guide_cue(cue:GuideCue): return guide_cue_store.add(cue)
@router.post("/guide-cues/reset",response_model=list[GuideCue])
def reset_guide_cues(): return guide_cue_store.reset()
@router.post("/score/validate")
def validate_score(score:ScoreJSON): return {"valid":True,"version":score.version,"events":len(score.drum_events),"guide_cues":len(score.guide_cues),"tempo_points":len(score.tempo_map)}

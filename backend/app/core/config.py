from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    app_name: str = "DrumScore AI"
    storage_dir: Path = Path("/tmp/drumscore_ai")
    separation_engine: str = "mock"  # mock | demucs
    demucs_model: str = "htdemucs"

settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)

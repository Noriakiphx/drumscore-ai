from app.core.config import settings
from .base import SeparationEngine
from .mock_engine import MockSeparationEngine
from .demucs_engine import DemucsSeparationEngine

def get_separation_engine() -> SeparationEngine:
    if settings.separation_engine == "demucs":
        return DemucsSeparationEngine(model=settings.demucs_model)
    return MockSeparationEngine()

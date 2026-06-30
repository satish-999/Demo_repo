from pathlib import Path

from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = BACKEND_ROOT / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    project_name: str = "cineweave-rae"
    database_url: str = f"sqlite:///{_DATA_DIR / 'cineweave.db'}"
    media_root: Path = PROJECT_ROOT / "test-media" / "uploads"
    enable_ml_semantic: bool = False
    ship_threshold: float = 75.0
    flag_threshold: float = 50.0
    sync_drift_threshold_ms: float = 120.0

    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
settings.media_root.mkdir(parents=True, exist_ok=True)

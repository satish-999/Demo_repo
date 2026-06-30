from pathlib import Path

from pydantic_settings import BaseSettings

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{_DATA_DIR / 'cineweave.db'}"
    media_root: Path = Path("./media")
    enable_ml_semantic: bool = False
    ship_threshold: float = 75.0
    flag_threshold: float = 50.0
    sync_drift_threshold_ms: float = 120.0

    class Config:
        env_file = ".env"


settings = Settings()
settings.media_root.mkdir(parents=True, exist_ok=True)

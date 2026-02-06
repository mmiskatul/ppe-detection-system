import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta


_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_env_path)


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


class Settings:
    mongo_url: str = _get_env("MONGO_URL", "mongodb://localhost:27017")
    mongo_db: str = _get_env("MONGO_DB", "ppe_detection")
    jwt_secret: str = _get_env("JWT_SECRET", "change-me")
    jwt_algorithm: str = _get_env("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(_get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    cors_origins: list[str] = [
        origin.strip()
        for origin in _get_env("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]
    admin_username: str = _get_env("ADMIN_USERNAME", "admin")
    admin_password: str = _get_env("ADMIN_PASSWORD", "admin123")
    mongo_timeout_ms: int = int(_get_env("MONGO_TIMEOUT_MS", "5000"))

    @property
    def access_token_expires(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)


settings = Settings()

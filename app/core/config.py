from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    finance_service_url: str

    upload_dir: Path = Path("uploads")
    max_file_size: int = 10 * 1024 * 1024
    allowed_types: set[str] = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    ocr_lang: str = "pt"

    finance_create_timeout: float = 10.0
    finance_process_timeout: float = 30.0

    class Config:
        env_file = ".env"


settings = Settings()
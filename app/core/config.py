from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = ""

    # Azure Document Intelligence (OCR)
    AZURE_API_KEY: str = ""
    AZURE_ENDPOINT: str = ""

    # Aplicación
    APP_NAME: str = "OCR Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Archivos
    UPLOAD_DIR: str = "tmp/uploads"
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Carga configuración desde variables de entorno y .env."""
    return Settings()
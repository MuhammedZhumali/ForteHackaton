from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):

    APP_NAME: str = "Forte Fraud Shield API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./forte_fraud.db"

    REDIS_URL: str = "redis://localhost:6379"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    ML_MODEL_PATH: str = "trained_model"
    DEFAULT_FRAUD_THRESHOLD: float = 0.5

    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

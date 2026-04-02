from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env")

    MAX_TIMEOUT: int = 300
    MAX_MEMORY: int = 4096
    MAX_CPU: float = 4.0
    MAX_QUEUE_SIZE: int = 500
    TASK_TTL: int = 1800

    SANDBOX_FUSION_URL: str = "http://sandbox-fusion:8080"


settings = Settings()

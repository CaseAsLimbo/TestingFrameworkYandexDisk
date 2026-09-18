from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки фреймворка."""
    base_url: str = "https://cloud-api.yandex.net"
    api_version: str = "v1"
    api_token: str = Field(min_lengt=1)

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()

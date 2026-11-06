"""Configuración de la app, leída desde backend/.env"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/broker.db"
    anthropic_api_key: str = ""
    claude_model_fast: str = "claude-haiku-5-5"
    claude_model_deep: str = "claude-sonnet-5-5"
    timezone: str = "Europe/Madrid"


settings = Settings()

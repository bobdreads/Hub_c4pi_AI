from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env.dev",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    env: str = "dev"
    debug: bool = False
    log_level: str = "INFO"

    # Discord
    discord_token: str
    discord_guild_id: int
    authorized_user_ids: list[int] = []

    # Database
    database_url: str

    # Redis
    redis_url: str
    redis_cache_url: str

    # AI APIs
    wavespeed_api_key: str
    anthropic_api_key: str = ""
    mureka_api_key: str = ""

    # --- A CORREÇÃO ESTÁ AQUI ---
    # Adicionamos as variáveis da APIFree como opcionais para o Pydantic parar de reclamar
    apifree_base_url: str = "https://api.apifree.ai/v1"
    apifree_api_key: str = ""

    # Security
    api_key_master: str

    # Streamlit
    streamlit_admin_pw_hash: str = ""

    @field_validator("authorized_user_ids", mode="before")
    @classmethod
    def parse_ids(cls, v):
        if isinstance(v, str):
            return [int(i.strip()) for i in v.split(",") if i.strip()]
        return v


settings = Settings()

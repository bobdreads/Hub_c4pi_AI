from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Raiz do projeto (duas pastas acima de backend/config.py)
ROOT_DIR = Path.cwd()


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

    # Database
    database_url: str

    # Redis
    redis_url: str
    redis_cache_url: str

    # AI APIs
    apifree_api_key: str
    anthropic_api_key: str = ""
    mureka_api_key: str = ""

    # Security
    api_key_master: str

    # Streamlit
    streamlit_admin_pw_hash: str = ""


settings = Settings()

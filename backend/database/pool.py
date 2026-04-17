import asyncpg
from config import settings
from utils.logging import get_logger

log = get_logger("database.pool")

_pool: asyncpg.Pool | None = None


async def create_pool() -> asyncpg.Pool:
    global _pool
    # Converte URL para formato asyncpg
    url = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql://")
    _pool = await asyncpg.create_pool(
        url,
        min_size=2,
        max_size=8,
        command_timeout=30,
    )
    log.info("Pool de conexões criado com sucesso")
    return _pool


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        return await create_pool()
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        log.info("Pool de conexões fechado")
        _pool = None

import uuid
import asyncpg
from utils.logging import get_logger

log = get_logger("database.queries.users")


async def get_or_create_user(pool: asyncpg.Pool, discord_id: str, username: str) -> dict:
    row = await pool.fetchrow(
        "SELECT * FROM users WHERE discord_id = $1", discord_id
    )
    if row:
        return dict(row)

    row = await pool.fetchrow(
        """
        INSERT INTO users (id, discord_id, username)
        VALUES ($1, $2, $3)
        RETURNING *
        """,
        uuid.uuid4(), discord_id, username     # ← gera o UUID aqui no Python
    )
    log.info(f"Novo usuário criado: {discord_id}")
    return dict(row)

import uuid
import asyncpg
from utils.logging import get_logger

log = get_logger("database.queries.chats")


async def get_or_create_chat(
    pool: asyncpg.Pool,
    user_id: str,
    channel_id: str,
    model: str = "openai/gpt-5.4-mini",
    system_prompt: str = "",
) -> dict:
    row = await pool.fetchrow(
        "SELECT * FROM chats WHERE user_id = $1 AND name = $2",
        user_id, channel_id
    )
    if row:
        return dict(row)

    row = await pool.fetchrow(
        """
        INSERT INTO chats (id, user_id, name, model, system_prompt, auto_save)
        VALUES ($1, $2, $3, $4, $5, true)
        RETURNING *
        """,
        uuid.uuid4(), user_id, channel_id, model, system_prompt   # ← UUID aqui
    )
    log.info(f"Novo chat criado: user={user_id} channel={channel_id}")
    return dict(row)


async def get_chat_history(
    pool: asyncpg.Pool,
    chat_id: str,
    limit: int = 20
) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT role, content FROM messages
        WHERE chat_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        chat_id, limit
    )
    return [dict(r) for r in reversed(rows)]


async def save_messages(
    pool: asyncpg.Pool,
    chat_id: str,
    user_id: str,
    prompt: str,
    response: str,
    model: str,
    prompt_tokens: int,
    output_tokens: int,
    latency_ms: int,
):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO messages (id, chat_id, user_id, role, content)
                VALUES ($1, $2, $3, 'user', $4)
                """,
                uuid.uuid4(), chat_id, user_id, prompt    # ← UUID aqui
            )
            await conn.execute(
                """
                INSERT INTO messages (id, chat_id, user_id, role, content, model,
                                      prompt_tokens, output_tokens, latency_ms)
                VALUES ($1, $2, $3, 'assistant', $4, $5, $6, $7, $8)
                """,
                uuid.uuid4(), chat_id, user_id, response, model,   # ← UUID aqui
                prompt_tokens, output_tokens, latency_ms
            )

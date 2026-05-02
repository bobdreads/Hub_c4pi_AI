import json
from schemas.params import LLMParams


async def get_user_params(db, user_id: str) -> LLMParams | None:
    """Carrega parâmetros LLM salvos do usuário."""
    row = await db.fetchrow(
        "SELECT llm_params FROM users WHERE discord_id = $1", user_id
    )
    if row and row["llm_params"]:
        try:
            return LLMParams(**json.loads(row["llm_params"]))
        except Exception:
            return None
    return None


async def save_user_params(db, user_id: str, params: LLMParams):
    """Salva parâmetros LLM do usuário."""
    await db.execute(
        """
        INSERT INTO users (discord_id, llm_params)
        VALUES ($1, $2)
        ON CONFLICT (discord_id) DO UPDATE SET llm_params = $2
        """,
        user_id, params.model_dump_json()
    )


async def get_or_create_chat(db, user_id: str, guild_id: str,
                             channel_id: str, model: str) -> str:
    """Retorna o chat_id ativo para este canal, ou cria um novo."""
    row = await db.fetchrow(
        """
        SELECT id FROM chats
        WHERE user_id = (SELECT id FROM users WHERE discord_id = $1)
          AND channel_id = $2
          AND active = true
        LIMIT 1
        """,
        user_id, channel_id
    )
    if row:
        return str(row["id"])

    # Criar novo chat
    row = await db.fetchrow(
        """
        INSERT INTO chats (user_id, guild_id, channel_id, model, name)
        VALUES (
          (SELECT id FROM users WHERE discord_id = $1),
          $2, $3, $4,
          'Chat ' || to_char(now(), 'DD/MM HH24:MI')
        )
        RETURNING id
        """,
        user_id, guild_id, channel_id, model
    )
    return str(row["id"])

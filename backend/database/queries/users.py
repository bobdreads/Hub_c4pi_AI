import json
from schemas.params import LLMParams
from utils.crypto import decrypt


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


async def get_or_create_user(db, discord_id: str, username: str = "User") -> dict:
    """
    Busca o usuário pelo discord_id. Se não existir, cria um novo na tabela users.
    Retorna o registro do banco contendo o 'id' (UUID).
    """
    # Tenta buscar o usuário existente
    user = await db.fetchrow(
        "SELECT id, discord_id, username FROM users WHERE discord_id = $1",
        str(discord_id)
    )

    if user:
        return user

    # Se não existir, cria um novo
    new_user = await db.fetchrow(
        """
        INSERT INTO users (discord_id, username)
        VALUES ($1, $2)
        RETURNING id, discord_id, username
        """,
        str(discord_id), username
    )

    return new_user


async def get_api_key(db, discord_id: str) -> str:
    """Busca a API Key criptografada do usuário e a descriptografa."""
    # Como a sua criptografia junta o IV e a chave numa string só,
    # presumimos que a coluna no banco se chama api_key_enc
    row = await db.fetchrow(
        "SELECT api_key_enc FROM users WHERE discord_id = $1",
        str(discord_id)
    )

    if not row or not row.get("api_key_enc"):
        raise ValueError(
            "API Key não configurada no banco. Use `/config api_key`")

    # Usa o seu método decrypt passando a string única
    return decrypt(row["api_key_enc"])

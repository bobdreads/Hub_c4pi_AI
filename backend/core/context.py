# backend/core/context.py
from utils.logging import get_logger

log = get_logger("core.context")


async def build_context(db, chat_id: str, limit: int = 20) -> list:
    """
    Busca as últimas `limit` mensagens do chat no banco
    e retorna no formato [{role, content}] para a API.
    """
    try:
        rows = await db.fetch(
            """
            SELECT role, content
            FROM messages
            WHERE chat_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            chat_id, limit
        )
        # rows vem do mais recente → inverte para ordem cronológica
        history = [{"role": r["role"], "content": r["content"]}
                   for r in reversed(rows)]
        return history
    except Exception as e:
        log.warning(f"Falha ao carregar contexto do chat {chat_id}: {e}")
        return []


async def save_message(db, chat_id: str, user_id: str, role: str, content: str,
                       model: str = None, tokens: int = 0):
    """Persiste uma mensagem no banco."""
    await db.execute(
        """
        INSERT INTO messages (chat_id, user_id, role, content, model, tokens)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        chat_id, user_id, role, content, model, tokens
    )

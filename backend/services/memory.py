from database.pool import get_pool
from database.queries.users import get_or_create_user
from database.queries.chats import get_or_create_chat, get_chat_history, save_messages
from adapters.base import GenerationRequest, GenerationResult
from utils.logging import get_logger

log = get_logger("services.memory")


class MemoryService:
    async def build_request_with_history(
        self,
        prompt: str,
        model: str,
        discord_id: str,
        username: str,
        channel_id: str,
        system_prompt: str = "",
    ) -> tuple[GenerationRequest, str, str]:
        """
        Retorna (request_com_historico, user_db_id, chat_db_id)
        """
        pool = await get_pool()

        # 1. Garante que o usuário existe no banco
        user = await get_or_create_user(pool, discord_id, username)
        user_id = str(user["id"])

        # 2. Garante que o chat existe
        chat = await get_or_create_chat(
            pool, user_id, channel_id, model, system_prompt
        )
        chat_id = str(chat["id"])

        # 3. Carrega histórico
        history = await get_chat_history(pool, chat_id, limit=20)

        # 4. Monta o request com histórico
        req = GenerationRequest(
            prompt=prompt,
            model=model,
            history=history,
            system_prompt=system_prompt,
            user_id=discord_id,
        )

        return req, user_id, chat_id

    async def save(
        self,
        chat_id: str,
        user_id: str,
        prompt: str,
        result: GenerationResult,
    ):
        pool = await get_pool()
        await save_messages(
            pool=pool,
            chat_id=chat_id,
            user_id=user_id,
            prompt=prompt,
            response=result.content,
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
        )
        log.info(f"Mensagens salvas: chat={chat_id}")


memory_service = MemoryService()

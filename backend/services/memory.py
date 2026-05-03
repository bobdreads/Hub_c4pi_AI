# services/memory.py
import httpx
import asyncio
import os
from dotenv import load_dotenv
from database.pool import get_pool
from database.queries.users import get_or_create_user
from database.queries.chats import get_or_create_chat, get_chat_history, save_messages
from database.queries.memory import insert_semantic_memory, search_semantic_memory
from adapters.base import GenerationRequest, GenerationResult
from utils.logging import get_logger

# Carrega as variáveis do arquivo .env para o sistema reconhecer
load_dotenv()

log = get_logger("services.memory")


class MemoryService:
    async def embed_text(self, text: str, api_key: str = None) -> list[float]:
        """Gera embeddings do texto chamando a API externa (OpenAI)."""
        # Puxa a chave da OpenAI direto do seu .env
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(
                "A chave OPENAI_API_KEY não foi encontrada no ambiente (.env).")

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {openai_key}"},
                json={"model": "text-embedding-3-small", "input": text}
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]

    async def search_semantic(self, user_id: str, query: str, api_key: str, limit: int = 3):
        """Busca contexto relevante baseado na query do usuário."""
        pool = await get_pool()
        try:
            embedding = await self.embed_text(query, api_key)
            return await search_semantic_memory(pool, user_id, embedding, limit)
        except Exception as e:
            log.error(f"Falha ao buscar memória semântica: {e}")
            raise  # Repassa o erro para o Discord mostrar a mensagem vermelha

    async def save_semantic(self, user_id: str, chat_id: str, content: str, api_key: str, metadata: dict = None):
        """Gera o vetor e salva a interação na memória de longo prazo."""
        if not content or len(content.strip()) < 5:
            return
        pool = await get_pool()
        try:
            embedding = await self.embed_text(content, api_key)
            await insert_semantic_memory(pool, user_id, chat_id, content, embedding, metadata)
            log.info(f"Memória semântica salva para user={user_id}")
        except Exception as e:
            log.error(f"Falha ao salvar memória semântica: {e}")
            raise  # Repassa o erro para o Discord em vez de fingir que deu certo

    async def build_request_with_history(
        self,
        prompt: str,
        model: str,
        discord_id: str,
        username: str,
        channel_id: str,
        system_prompt: str = "",
        memory_injection: bool = False,
        api_key: str = None
    ) -> tuple[GenerationRequest, str, str]:
        """Retorna (request_com_historico, user_db_id, chat_db_id) com injeção semântica opcional."""
        pool = await get_pool()

        # 1. Banco: Usuário e Chat
        user = await get_or_create_user(pool, discord_id, username)
        user_id = str(user["id"])
        chat = await get_or_create_chat(pool, user_id, channel_id, model, system_prompt)
        chat_id = str(chat["id"])

        # 2. Histórico de Curto Prazo (Últimas 20 msgs)
        history = await get_chat_history(pool, chat_id, limit=20)

        # 3. Histórico de Longo Prazo (Injeção Semântica pgvector)
        final_system_prompt = system_prompt
        if memory_injection and api_key:
            memories = await self.search_semantic(user_id, prompt, api_key)
            if memories:
                ctx = "\n".join(
                    f"[Lembrança {i+1}]: {m['content']}" for i, m in enumerate(memories))
                final_system_prompt += f"\n\n## Contexto Relevante do Passado:\n{ctx}"

        # 4. Monta o Request
        req = GenerationRequest(
            prompt=prompt,
            model=model,
            history=history,
            system_prompt=final_system_prompt,
            user_id=discord_id,
        )

        return req, user_id, chat_id

    async def save(
        self,
        chat_id: str,
        user_id: str,
        prompt: str,
        result: GenerationResult,
        auto_save_memory: bool = False,
        api_key: str = None
    ):
        """Salva a mensagem no histórico e, opcionalmente, na memória vetorial."""
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

        # Salva em background (fire-and-forget) na memória vetorial
        if auto_save_memory and api_key:
            interaction = f"User: {prompt}\nAssistant: {result.content}"
            asyncio.create_task(
                self.save_semantic(user_id, chat_id, interaction, api_key)
            )


memory_service = MemoryService()

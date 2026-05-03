import asyncio
from adapters.factory import AdapterFactory
from core.context import build_context, save_message
from schemas.params import LLMParams
from adapters.base import GenerationRequest
from services.memory import memory_service
from utils.logging import get_logger

log = get_logger("services.generation")


class GenerationService:
    def __init__(self, db, redis=None):
        self.db = db
        self.redis = redis

    async def run(
        self,
        prompt:   str,
        user_id:  str,
        chat_id:  any,
        params:   LLMParams,
        api_key:  str,
        files:    list = None,
    ):
        if hasattr(chat_id, "get"):
            chat_id = str(chat_id.get("id", chat_id))
        else:
            chat_id = str(chat_id)

        # 1. Carregar histórico do banco (Curto Prazo)
        history = await build_context(self.db, chat_id, limit=params.context_limit)

        # 2. Injeção de Memória Semântica (Longo Prazo)
        final_system_prompt = params.system_prompt or "Você é o Capybara AI, um assistente amigável e prestativo."

        injetar_memoria = getattr(params, "memory_injection", True)

        # Variável nova: O que a IA realmente vai ler
        prompt_enviado = f"{prompt}\n\n---\n*Sussurro do Sistema: Você recuperou as seguintes memórias do banco de dados:*\n{ctx}\n*Instrução restrita: Responda de forma natural e use APENAS as memórias acima que tiverem relação direta com a pergunta atual do usuário. Ignore completamente as memórias irrelevantes.*"

        if injetar_memoria is not False and api_key:
            try:
                memories = await memory_service.search_semantic(user_id, prompt, api_key, limit=3)
                if memories:
                    ctx = "\n".join(
                        f"- {m['content']}" for i, m in enumerate(memories))
                    # O pulo do gato: Colocamos a memória no final da sua pergunta!
                    prompt_enviado = f"{prompt}\n\n---\n*Sussurro do Sistema: Você lembrou das seguintes informações sobre este usuário:*\n{ctx}\n*Responda usando essas informações de forma natural e amigável.*"
                    print(f"\n[!!!] MEMÓRIA COLADA NA PERGUNTA: {ctx}\n")
            except Exception as e:
                log.error(f"Erro ao buscar memória: {e}")

        # 3. Montar request
        req = GenerationRequest(
            prompt=prompt_enviado,  # <-- Mandamos a pergunta com o sussurro!
            model=params.model,
            history=history,
            system=final_system_prompt,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            top_p=params.top_p,
            frequency_penalty=params.frequency_penalty,
            presence_penalty=params.presence_penalty,
            files=files or [],
            user_id=user_id,
            chat_id=chat_id,
            api_key=api_key,
        )

        # 4. Chamar o adapter
        adapter = AdapterFactory.get(params.model)
        result = await adapter.generate(req)

        # 5. Persistir no banco
        try:
            await save_message(self.db, chat_id, user_id,
                               role="user", content=prompt,
                               tokens=result.prompt_tokens)
            if result.success:
                await save_message(self.db, chat_id, user_id,
                                   role="assistant", content=result.text,
                                   model=result.model, tokens=result.output_tokens)

                # 6. Auto-save na memória semântica
                if getattr(params, "auto_save", False) and api_key:
                    interaction = f"User: {prompt}\nAssistant: {result.text}"
                    asyncio.create_task(
                        memory_service.save_semantic(
                            user_id=user_id,
                            chat_id=chat_id,
                            content=interaction,
                            api_key=api_key
                        )
                    )
        except Exception as e:
            log.warning(f"Falha ao persistir mensagens/memória: {e}")

        return result

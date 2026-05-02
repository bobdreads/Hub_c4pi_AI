class GenerationService:
    def __init__(self, db, redis=None):
        self.db = db
        self.redis = redis

    async def run(
        self,
        prompt:   str,
        user_id:  str,
        chat_id:  str,
        params:   LLMParams,
        files:    list = None,   # lista de AttachedFile
    ):
        # 1. Carregar histórico do banco
        history = await build_context(self.db, chat_id, limit=params.context_limit)

        # 2. Montar request
        req = GenerationRequest(
            prompt=prompt,
            model=params.model,
            history=history,
            system=params.system_prompt,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            top_p=params.top_p,
            frequency_penalty=params.frequency_penalty,
            presence_penalty=params.presence_penalty,
            files=files or [],
            user_id=user_id,
            chat_id=chat_id,
        )

        # 3. Chamar o adapter
        adapter = AdapterFactory.get(params.model)
        result = await adapter.generate(req)

        # 4. Persistir no banco (mesmo se deu erro parcial)
        try:
            await save_message(self.db, chat_id, user_id,
                               role="user", content=prompt,
                               tokens=result.prompt_tokens)
            if result.success:
                await save_message(self.db, chat_id, user_id,
                                   role="assistant", content=result.text,
                                   model=result.model, tokens=result.output_tokens)
        except Exception as e:
            log.warning(f"Falha ao persistir mensagens: {e}")

        return result

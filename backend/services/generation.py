import asyncio
from adapters.factory import AdapterFactory
from adapters.base import GenerationRequest, GenerationResult
from utils.logging import get_logger

log = get_logger("services.generation")


class GenerationService:
    async def run(self, req: GenerationRequest) -> GenerationResult:
        log.info(f"Iniciando geração: model={req.model} user={req.user_id}")

        adapter = AdapterFactory.get(req.model)
        result = await adapter.generate(req)

        log.info(
            f"Geração concluída: model={req.model} "
            f"tokens={result.prompt_tokens}+{result.output_tokens} "
            f"latency={result.latency_ms}ms"
        )
        return result

    async def run_image(self, prompt: str, model: str = "dall-e-3") -> GenerationResult:
        log.info(f"Iniciando geração de imagem: model={model}")
        adapter = AdapterFactory.get(model)
        result = await adapter.generate_image(prompt, model)
        log.info(f"Imagem gerada: latency={result.latency_ms}ms")
        return result


generation_service = GenerationService()

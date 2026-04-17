import time
import httpx
from adapters.base import GenerationRequest, GenerationResult
from config import settings
from utils.logging import get_logger

log = get_logger("adapters.nano")

BASE_URL = "https://api.apifree.ai/v1"


class NanoAdapter:
    def __init__(self):
        self.api_key = settings.apifree_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(self, req: GenerationRequest) -> GenerationResult:
        start = time.time()

        messages = []
        if req.system_prompt:
            messages.append({"role": "system", "content": req.system_prompt})
        messages.extend(req.history)
        messages.append({"role": "user", "content": req.prompt})

        payload = {
            "model": req.model,
            "messages": messages,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = int((time.time() - start) * 1000)
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return GenerationResult(
            content=content,
            model=req.model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            latency_ms=latency_ms,
        )

    async def generate_image(self, prompt: str, model: str = "openai/gpt-image-1.5") -> GenerationResult:
        start = time.time()

        payload = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{BASE_URL}/model/{model}",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            log.info(f"Resposta imagem: {data}")

        latency_ms = int((time.time() - start) * 1000)
        image_url = data.get("url") or data.get("data", [{}])[0].get("url", "")

        return GenerationResult(
            content=prompt,
            model=model,
            latency_ms=latency_ms,
            media_url=image_url,
            media_type="image",
        )

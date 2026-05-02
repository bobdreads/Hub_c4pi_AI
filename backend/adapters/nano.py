import httpx
import base64
import time
from adapters.base import BaseAdapter, GenerationRequest, AttachedFile
from schemas.response import GenerationResult
from config import settings
from utils.logging import get_logger

log = get_logger("adapters.nano")

BASE_URL = "https://llm.wavespeed.ai/v1"
_IMAGE_MIMES = {"image/png", "image/jpeg", "image/gif", "image/webp"}


class NanoAdapter:
    def __init__(self):
        self.api_key = settings.wavespeed_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(self, req: GenerationRequest) -> GenerationResult:
        start = time.monotonic()
        messages = self._build_messages(req)

        payload = {
            "model":             req.model,
            "messages":          messages,
            "temperature":       req.temperature,
            "max_tokens":        req.max_tokens,
            "top_p":             req.top_p,
            "frequency_penalty": req.frequency_penalty,
            "presence_penalty":  req.presence_penalty,
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(
                    f"{settings.apifree_base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.apifree_api_key}"},
                    json=payload,
                )
                r.raise_for_status()
                data = r.json()

            choice = data["choices"][0]
            usage = data.get("usage", {})
            latency = (time.monotonic() - start) * 1000

            return GenerationResult(
                text=choice["message"]["content"],
                model=data.get("model", req.model),
                prompt_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                latency_ms=latency,
                finish_reason=choice.get("finish_reason", "stop"),
            )

        except httpx.HTTPStatusError as e:
            log.error(
                f"HTTP {e.response.status_code} na API: {e.response.text[:200]}")
            return GenerationResult(error=f"Erro da API: HTTP {e.response.status_code}")
        except Exception as e:
            log.error(f"Erro inesperado: {e}")
            return GenerationResult(error=str(e))

    def _build_messages(self, req: GenerationRequest) -> list:
        messages = []

        # System prompt
        if req.system:
            messages.append({"role": "system", "content": req.system})

        # Histórico de conversa
        messages.extend(req.history)

        # Mensagem atual — pode ter texto + arquivos
        user_content = self._build_user_content(req)
        messages.append({"role": "user", "content": user_content})

        return messages

    def _build_user_content(self, req: GenerationRequest):
        """Monta o content do usuário: texto puro ou lista multimodal."""
        if not req.files:
            return req.prompt  # simples, sem arquivos

        # Com arquivos: montar lista de parts
        parts = []

        # Texto primeiro
        if req.prompt:
            parts.append({"type": "text", "text": req.prompt})

        for f in req.files:
            if f.mime_type in _IMAGE_MIMES:
                # Imagem → image_url com base64
                b64 = base64.b64encode(f.data).decode()
                parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{f.mime_type};base64,{b64}"
                    }
                })
            elif f.text_content:
                # PDF/CSV/TXT → injetar como texto
                parts.append({
                    "type": "text",
                    "text": f"\n--- Arquivo: {f.filename} ---\n{f.text_content}\n---"
                })

        return parts if parts else req.prompt

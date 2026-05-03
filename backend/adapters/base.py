from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod


@dataclass
class AttachedFile:
    """Arquivo enviado pelo usuário junto com o prompt."""
    filename:    str
    mime_type:   str          # ex: "image/png", "application/pdf", "text/plain"
    data:        bytes        # conteúdo raw do arquivo
    text_content: Optional[str] = None  # extraído de PDF/CSV/TXT


@dataclass
class GenerationRequest:
    prompt:       str
    model:        str = "openai/gpt-5.4-mini"
    history:      list = field(default_factory=list)  # [{role, content}, ...]
    system:       Optional[str] = None
    temperature:  float = 0.7
    max_tokens:   int = 2048
    top_p:        float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty:  float = 0.0
    files:        list = field(default_factory=list)  # lista de AttachedFile
    user_id:      Optional[str] = None
    chat_id:      Optional[str] = None
    api_key:      Optional[str] = None

# === AQUI ESTÁ A CORREÇÃO MÁGICA ===


@dataclass
class GenerationResult:
    text: str                       # Trocamos 'content' por 'text'
    model: str
    prompt_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    success: bool = True            # Adicionamos a flag de sucesso
    # Adicionamos o campo de erro (caso precise)
    error: Optional[str] = None
    finish_reason: str = "stop"     # Adicionamos o motivo da finalização


class BaseAdapter(ABC):
    @abstractmethod
    async def generate(self, req: GenerationRequest) -> GenerationResult:
        ...

    async def health_check(self) -> bool:
        return True

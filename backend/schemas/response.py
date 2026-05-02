from pydantic import BaseModel
from typing import Optional, Literal
from dataclasses import dataclass, field


@dataclass
class GenerationResult:
    """Resultado unificado de qualquer geração."""
    text:           Optional[str] = None
    model:          str = ""
    prompt_tokens:  int = 0
    output_tokens:  int = 0
    latency_ms:     float = 0.0
    finish_reason:  str = "stop"
    error:          Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.output_tokens

    @property
    def success(self) -> bool:
        return self.error is None and self.text is not None

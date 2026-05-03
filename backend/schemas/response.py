from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationResult:
    text: str = ""
    model: str = ""
    prompt_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    finish_reason: str = "stop"

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.output_tokens

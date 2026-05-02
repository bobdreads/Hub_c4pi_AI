from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod


@dataclass
class GenerationRequest:
    prompt: str
    model: str = "gpt-4o"
    history: list[dict] = field(default_factory=list)
    system_prompt: str = ""
    max_tokens: int = 2048
    temperature: float = 0.7
    user_id: str = ""


@dataclass
class GenerationResult:
    content: str
    model: str
    prompt_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0

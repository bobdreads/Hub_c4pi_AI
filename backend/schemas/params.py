from pydantic import BaseModel, Field
from typing import Optional


class LLMParams(BaseModel):
    """Parâmetros configuráveis por usuário/chat para chamadas LLM."""

    model: str = "openai/gpt-5.4-mini"

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Criatividade da resposta. 0=determinístico, 2=muito criativo"
    )

    max_tokens: int = Field(
        default=2048,
        ge=64,
        le=32000,
        description="Máximo de tokens na resposta"
    )

    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling. Reduzir para respostas mais focadas"
    )

    frequency_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Penaliza repetição de palavras frequentes"
    )

    presence_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Penaliza repetição de tópicos já mencionados"
    )

    system_prompt: Optional[str] = Field(
        default=None,
        max_length=4000,
        description="Instrução de sistema personalizada"
    )

    context_limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Quantas mensagens anteriores incluir no contexto"
    )

    def to_api_dict(self) -> dict:
        """Converte para o formato esperado pela API."""
        d = {
            "temperature":         self.temperature,
            "max_tokens":          self.max_tokens,
            "top_p":               self.top_p,
            "frequency_penalty":   self.frequency_penalty,
            "presence_penalty":    self.presence_penalty,
        }
        return {k: v for k, v in d.items() if v is not None}


# Presets prontos para o usuário escolher
PARAM_PRESETS = {
    "preciso": LLMParams(temperature=0.1, top_p=0.9,  frequency_penalty=0.0),
    "normal":  LLMParams(temperature=0.7, top_p=1.0,  frequency_penalty=0.0),
    "criativo": LLMParams(temperature=1.2, top_p=0.95, frequency_penalty=0.3),
    "codigo":  LLMParams(temperature=0.2, top_p=0.95, frequency_penalty=0.1,
                         system_prompt="Você é um assistente de programação especialista. "
                                       "Responda sempre com código limpo e bem comentado."),
    "resumo":  LLMParams(temperature=0.3, max_tokens=512,
                         system_prompt="Responda de forma extremamente concisa e direta."),
}

from adapters.nano import NanoAdapter
from utils.logging import get_logger

log = get_logger("adapters.factory")

_REGISTRY = {
    # ── OpenAI ──────────────────────────────
    "openai/gpt-5.4-mini":      NanoAdapter,
    "openai/gpt-5.4-nano":      NanoAdapter,
    "openai/gpt-5.4":           NanoAdapter,
    "openai/gpt-5.2":           NanoAdapter,
    "openai/gpt-5.1":           NanoAdapter,
    "openai/gpt-5":             NanoAdapter,
    "openai/gpt-5-mini":        NanoAdapter,
    "openai/gpt-5-nano":        NanoAdapter,
    "openai/gpt-4o":            NanoAdapter,
    "openai/gpt-4o-mini":       NanoAdapter,
    "openai/gpt-4.1":           NanoAdapter,
    "openai/gpt-4.1-mini":      NanoAdapter,
    "openai/gpt-4.1-nano":      NanoAdapter,
    "openai/o3":                NanoAdapter,
    "openai/o3-mini":           NanoAdapter,
    "openai/o4-mini":           NanoAdapter,
    "openai/o4-mini-high":      NanoAdapter,

    # ── Anthropic ───────────────────────────
    "anthropic/claude-haiku-4.5":      NanoAdapter,
    "anthropic/claude-sonnet-4.5":     NanoAdapter,
    "anthropic/claude-sonnet-4.6":     NanoAdapter,
    "anthropic/claude-opus-4.5":       NanoAdapter,
    "anthropic/claude-opus-4.6":       NanoAdapter,
    "anthropic/claude-opus-4.7":       NanoAdapter,
    "anthropic/claude-3.7-sonnet":     NanoAdapter,
    "anthropic/claude-3.7-sonnet:thinking": NanoAdapter,

    # ── Google ──────────────────────────────
    "google/gemini-2.5-pro":                        NanoAdapter,
    "google/gemini-2.5-flash":                      NanoAdapter,
    "google/gemini-2.5-flash-lite":                 NanoAdapter,
    "google/gemini-3-flash-preview":                NanoAdapter,
    "google/gemini-3.1-pro-preview":                NanoAdapter,
    "google/gemini-3.1-flash-lite-preview":         NanoAdapter,
    "google/gemini-2.0-flash-001":                  NanoAdapter,

    # ── x.AI ────────────────────────────────
    "x-ai/grok-4":              NanoAdapter,
    "x-ai/grok-4-fast":         NanoAdapter,
    "x-ai/grok-4.1-fast":       NanoAdapter,
    "x-ai/grok-3":              NanoAdapter,
    "x-ai/grok-3-mini":         NanoAdapter,
    "x-ai/grok-code-fast-1":    NanoAdapter,

    # ── DeepSeek ────────────────────────────
    "deepseek/deepseek-v3.2":           NanoAdapter,
    "deepseek/deepseek-v3.2-exp":       NanoAdapter,
    "deepseek/deepseek-chat-v3.1":      NanoAdapter,
    "deepseek/deepseek-r1":             NanoAdapter,
    "deepseek/deepseek-r1-0528":        NanoAdapter,

    # ── Meta Llama ──────────────────────────
    "meta-llama/llama-4-maverick":          NanoAdapter,
    "meta-llama/llama-4-scout":             NanoAdapter,
    "meta-llama/llama-3.3-70b-instruct":    NanoAdapter,
    "meta-llama/llama-3.1-70b-instruct":    NanoAdapter,

    # ── Qwen ────────────────────────────────
    "qwen/qwen3-235b-a22b":         NanoAdapter,
    "qwen/qwen3-32b":               NanoAdapter,
    "qwen/qwen3-coder":             NanoAdapter,
    "qwen/qwen3-coder-next":        NanoAdapter,
    "qwen/qwen3.5-397b-a17b":       NanoAdapter,
    "qwen/qwen3-max":               NanoAdapter,
    "qwen/qwen3-max-thinking":      NanoAdapter,

    # ── Mistral ─────────────────────────────
    "mistralai/mistral-large-2512":             NanoAdapter,
    "mistralai/mistral-medium-3.1":             NanoAdapter,
    "mistralai/devstral-small":                 NanoAdapter,
    "mistralai/codestral-2508":                 NanoAdapter,

    # ── Moonshot ────────────────────────────
    "moonshotai/kimi-k2.5":         NanoAdapter,
    "moonshotai/kimi-k2-thinking":  NanoAdapter,

    # ── Perplexity ──────────────────────────
    "perplexity/sonar":             NanoAdapter,
    "perplexity/sonar-pro":         NanoAdapter,

    # ── Outros ──────────────────────────────
    "minimax/minimax-m2.5":         NanoAdapter,
    "minimax/minimax-m2.7":         NanoAdapter,
    "z-ai/glm-5":                   NanoAdapter,
    "z-ai/glm-4.5":                 NanoAdapter,
    "amazon/nova-pro-v1":           NanoAdapter,
    "amazon/nova-premier-v1":       NanoAdapter,
    "microsoft/phi-4":              NanoAdapter,
}

DEFAULT_MODEL = "openai/gpt-5.4-mini"

MODEL_CATALOG = {
    "OpenAI": [
        ("openai/gpt-5.4-mini",  "GPT 5.4 Mini  — ⚡ Rápido e barato"),
        ("openai/gpt-5.4-nano",  "GPT 5.4 Nano  — ⚡⚡ Ultrarrápido"),
        ("openai/gpt-5.4",       "GPT 5.4       — 🧠 Avançado"),
        ("openai/gpt-5.2",       "GPT 5.2       — 🧠 Avançado"),
        ("openai/gpt-5",         "GPT 5         — 🧠🧠 Topo"),
        ("openai/gpt-4o",        "GPT 4o        — 🔁 Clássico"),
        ("openai/gpt-4.1",       "GPT 4.1       — 🔁 Clássico"),
        ("openai/o4-mini",       "o4 Mini       — 🤔 Raciocínio"),
        ("openai/o3",            "o3            — 🤔🤔 Raciocínio avançado"),
    ],
    "Anthropic": [
        ("anthropic/claude-haiku-4.5",  "Claude Haiku 4.5  — ⚡ Rápido"),
        ("anthropic/claude-sonnet-4.6",
         "Claude Sonnet 4.6 — 🏆 Melhor custo-benefício"),
        ("anthropic/claude-opus-4.7",   "Claude Opus 4.7   — 🧠🧠 Topo"),
        ("anthropic/claude-3.7-sonnet:thinking",
         "Claude 3.7 Thinking — 🤔 Raciocínio"),
    ],
    "Google": [
        ("google/gemini-2.5-flash",          "Gemini 2.5 Flash     — ⚡ Rápido"),
        ("google/gemini-2.5-flash-lite",     "Gemini 2.5 Flash Lite — ⚡⚡"),
        ("google/gemini-2.5-pro",            "Gemini 2.5 Pro       — 🧠 Avançado"),
        ("google/gemini-3-flash-preview",    "Gemini 3 Flash       — 🆕 Novo"),
        ("google/gemini-3.1-pro-preview",    "Gemini 3.1 Pro       — 🆕🧠 Topo"),
    ],
    "xAI": [
        ("x-ai/grok-4-fast",      "Grok 4 Fast     — ⚡ Rápido"),
        ("x-ai/grok-4",           "Grok 4          — 🧠🧠 Topo"),
        ("x-ai/grok-code-fast-1", "Grok Code Fast  — 💻 Código"),
    ],
    "DeepSeek": [
        ("deepseek/deepseek-chat-v3.1",  "DeepSeek v3.1      — ⚡ Rápido"),
        ("deepseek/deepseek-v3.2",       "DeepSeek v3.2      — 🧠 Avançado"),
        ("deepseek/deepseek-r1-0528",    "DeepSeek R1        — 🤔 Raciocínio"),
    ],
    "Meta": [
        ("meta-llama/llama-4-scout",          "Llama 4 Scout   — ⚡ Rápido"),
        ("meta-llama/llama-4-maverick",       "Llama 4 Maverick — 🧠 Avançado"),
        ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B   — 🔁 Clássico"),
    ],
    "Qwen": [
        ("qwen/qwen3-coder-next",     "Qwen3 Coder       — 💻 Código"),
        ("qwen/qwen3-235b-a22b",      "Qwen3 235B        — 🧠 Grande escala"),
        ("qwen/qwen3-max-thinking",   "Qwen3 Max Thinking — 🤔 Raciocínio"),
        ("qwen/qwen3.5-397b-a17b",    "Qwen3.5 397B      — 🧠🧠 Topo"),
    ],
    "Outros": [
        ("moonshotai/kimi-k2.5",      "Kimi K2.5         — 🌐 Busca web"),
        ("mistralai/mistral-large-2512", "Mistral Large  — 🧠 Avançado"),
        ("perplexity/sonar-pro",      "Sonar Pro         — 🔍 Pesquisa"),
        ("minimax/minimax-m2.7",      "MiniMax M2.7"),
        ("z-ai/glm-5",                "GLM-5"),
        ("amazon/nova-premier-v1",    "Nova Premier      — 🧠 AWS"),
    ],
}


class AdapterFactory:
    @staticmethod
    def get(model: str) -> NanoAdapter:
        adapter_class = _REGISTRY.get(model)
        if not adapter_class:
            raise ValueError(
                f"Modelo não suportado: `{model}`. Use `/modelos` para ver a lista.")
        log.info(f"Adapter criado para modelo: {model}")
        return adapter_class()

    @staticmethod
    def list_models() -> dict:
        return MODEL_CATALOG

    @staticmethod
    def is_valid(model: str) -> bool:
        return model in _REGISTRY

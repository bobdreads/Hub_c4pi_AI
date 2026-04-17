from adapters.nano import NanoAdapter
from utils.logging import get_logger

log = get_logger("adapters.factory")

# ──────────────────────────────────────────────
# REGISTRY — Modelos LLM disponíveis na apifree.ai
# ──────────────────────────────────────────────

_REGISTRY = {

    # ── OpenAI ──────────────────────────────
    "openai/gpt-5.4-mini":  NanoAdapter,
    "openai/gpt-5.4-nano":  NanoAdapter,
    "openai/gpt-5.4":       NanoAdapter,
    "openai/gpt-5.2":       NanoAdapter,
    "openai/gpt-5":         NanoAdapter,
    "openai/gpt-5-mini":    NanoAdapter,
    "openai/gpt-5-nano":    NanoAdapter,
    "openai/gpt-4o":        NanoAdapter,
    "openai/gpt-4o-mini":   NanoAdapter,
    "openai/gpt-4.1":       NanoAdapter,
    "openai/gpt-4.1-mini":  NanoAdapter,

    # ── Anthropic ───────────────────────────
    "anthropic/claude-sonnet-4.6": NanoAdapter,
    "anthropic/claude-sonnet-4.5": NanoAdapter,
    "anthropic/claude-haiku-4.5":  NanoAdapter,
    "anthropic/claude-opus-4.6":   NanoAdapter,
    "anthropic/claude-opus-4.5":   NanoAdapter,

    # ── Google ──────────────────────────────
    "google/gemini-3.1-pro/ai-studio":    NanoAdapter,
    "google/gemini-3.1-pro/on-demand":    NanoAdapter,
    "google/gemini-3.1-pro/us-east":      NanoAdapter,
    "google/gemini-3-flash/ai-studio":    NanoAdapter,
    "google/gemini-3-flash/on-demand":    NanoAdapter,
    "google/gemini-3-flash/us-east":      NanoAdapter,
    "google/gemini-2.5-pro/ai-studio":    NanoAdapter,
    "google/gemini-2.5-pro/on-demand":    NanoAdapter,
    "google/gemini-2.5-pro":              NanoAdapter,
    "google/gemini-2.5-flash/ai-studio":  NanoAdapter,
    "google/gemini-2.5-flash/on-demand":  NanoAdapter,
    "google/gemini-2.5-flash":            NanoAdapter,
    "google/gemini-2.5-flash-lite":       NanoAdapter,

    # ── x.AI ────────────────────────────────
    "xai/grok-4":           NanoAdapter,
    "xai/grok-4-fast":      NanoAdapter,
    "xai/grok-4.1-fast":    NanoAdapter,
    "xai/grok-code-fast-1": NanoAdapter,

    # ── Moonshot ────────────────────────────
    "moonshotai/kimi-k2.5": NanoAdapter,
    "moonshotai/kimi-k2":   NanoAdapter,

    # ── Qwen ────────────────────────────────
    "qwen/qwen3.5-397b-a17b":  NanoAdapter,
    "qwen/qwen3-32b":          NanoAdapter,
    "qwen/qwen3-coder-next":   NanoAdapter,

    # ── Outros ──────────────────────────────
    "zai-org/glm-5":           NanoAdapter,
    "minimax/minimax-m2.5":    NanoAdapter,
    "bytedance/seed-1.8":      NanoAdapter,
}

# Modelo padrão (rápido e barato)
DEFAULT_MODEL = "openai/gpt-5.4-mini"

# Catálogo legível para o comando /modelos no Discord
MODEL_CATALOG = {
    "OpenAI": [
        ("openai/gpt-5.4-mini",  "GPT 5.4 Mini  — ⚡ Rápido e barato"),
        ("openai/gpt-5.4-nano",  "GPT 5.4 Nano  — ⚡⚡ Mais rápido"),
        ("openai/gpt-5.4",       "GPT 5.4       — 🧠 Avançado"),
        ("openai/gpt-5.2",       "GPT 5.2       — 🧠 Avançado"),
        ("openai/gpt-5",         "GPT 5         — 🧠🧠 Topo"),
        ("openai/gpt-4o",        "GPT 4o        — 🔁 Clássico"),
        ("openai/gpt-4.1",       "GPT 4.1       — 🔁 Clássico"),
    ],
    "Anthropic": [
        ("anthropic/claude-sonnet-4.6",
         "Claude Sonnet 4.6 — 🏆 Melhor custo-benefício"),
        ("anthropic/claude-sonnet-4.5", "Claude Sonnet 4.5"),
        ("anthropic/claude-haiku-4.5",  "Claude Haiku 4.5  — ⚡ Rápido"),
        ("anthropic/claude-opus-4.6",   "Claude Opus 4.6   — 🧠🧠 Topo"),
        ("anthropic/claude-opus-4.5",   "Claude Opus 4.5   — 🧠🧠 Topo"),
    ],
    "Google": [
        ("google/gemini-2.5-pro",         "Gemini 2.5 Pro   — 🧠 Avançado"),
        ("google/gemini-2.5-flash",        "Gemini 2.5 Flash — ⚡ Rápido"),
        ("google/gemini-2.5-flash-lite",   "Gemini 2.5 Flash Lite — ⚡⚡"),
        ("google/gemini-3-flash/on-demand", "Gemini 3 Flash   — 🆕 Novo"),
        ("google/gemini-3.1-pro/on-demand", "Gemini 3.1 Pro   — 🆕🧠 Topo"),
    ],
    "xAI": [
        ("xai/grok-4",        "Grok 4      — 🧠🧠 Topo"),
        ("xai/grok-4-fast",   "Grok 4 Fast — ⚡ Rápido"),
    ],
    "Outros": [
        ("moonshotai/kimi-k2.5",        "Kimi K2.5"),
        ("qwen/qwen3-32b",              "Qwen3 32B"),
        ("qwen/qwen3.5-397b-a17b",      "Qwen3.5 397B"),
        ("zai-org/glm-5",               "GLM 5"),
        ("minimax/minimax-m2.5",        "MiniMax M2.5"),
        ("bytedance/seed-1.8",          "Seed 1.8"),
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

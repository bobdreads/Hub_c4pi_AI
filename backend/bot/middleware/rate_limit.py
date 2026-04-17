import time
from functools import wraps
import discord
from utils.logging import get_logger

log = get_logger("bot.middleware.rate_limit")

# Estrutura: {user_id: {modalidade: [timestamps]}}
_rate_store: dict = {}

# Limites por modalidade (requisições por 60 segundos)
LIMITS = {
    "llm": 10,
    "imagem": 5,
    "audio": 3,
    "video": 2,
}


def rate_limit_check(modality: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: discord.ApplicationContext, *args, **kwargs):
            user_id = ctx.author.id
            now = time.time()
            window = 60  # segundos

            if user_id not in _rate_store:
                _rate_store[user_id] = {}
            if modality not in _rate_store[user_id]:
                _rate_store[user_id][modality] = []

            # Remove timestamps fora da janela
            _rate_store[user_id][modality] = [
                t for t in _rate_store[user_id][modality]
                if now - t < window
            ]

            limit = LIMITS.get(modality, 5)
            if len(_rate_store[user_id][modality]) >= limit:
                log.info(
                    f"Rate limit atingido: user={user_id} modality={modality}")
                await ctx.respond(
                    f"⏳ Limite atingido para `{modality}`. Aguarde um momento.",
                    ephemeral=True
                )
                return

            _rate_store[user_id][modality].append(now)
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator

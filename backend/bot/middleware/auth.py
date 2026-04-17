import discord
from functools import wraps
from config import settings
from utils.logging import get_logger

log = get_logger("bot.middleware.auth")


def require_authorized(func):
    @wraps(func)
    async def wrapper(self, ctx: discord.ApplicationContext, *args, **kwargs):
        if ctx.author.id not in settings.authorized_user_ids:
            log.info(f"Acesso negado para user_id={ctx.author.id}")
            return  # Rejeita silenciosamente
        return await func(self, ctx, *args, **kwargs)
    return wrapper

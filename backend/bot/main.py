import os
import sys

# isort: skip_file
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".."))

import discord  # noqa: E402
from config import settings  # noqa: E402
from utils.logging import get_logger  # noqa: E402

from database.pool import create_pool, close_pool  # noqa: E402


log = get_logger("bot.main")


class CapybaraBot(discord.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(intents=intents)

    async def on_ready(self):
        await create_pool()
        log.info(f"Bot online como {self.user}")
        await self.sync_commands(guild_ids=[settings.discord_guild_id])
        log.info("Comandos slash sincronizados!")

    async def close(self):                           # ← ADICIONA ESSE BLOCO
        await close_pool()
        await super().close()

    async def on_application_command_error(self, ctx, error):
        if isinstance(error, discord.ApplicationCommandError):
            await ctx.respond(f"❌ {str(error)}", ephemeral=True)
        else:
            log.error(f"Erro inesperado: {error}")
            await ctx.respond("❌ Ocorreu um erro inesperado.", ephemeral=True)


def main():
    bot = CapybaraBot()
    extensions = ["bot.cogs.chat",
                  "bot.cogs.config_cog",
                  "bot.cogs.generate",
                  "bot.cogs.memory"
                  ]

    for ext in extensions:
        bot.load_extension(ext)
        log.info(f"Extensao carregada: {ext}")
    bot.run(settings.discord_token)


if __name__ == "__main__":
    main()

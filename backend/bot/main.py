import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import discord
from config import settings
from utils.logging import get_logger

log = get_logger("bot.main")


class CapybaraBot(discord.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(intents=intents)

    async def on_ready(self):
        log.info(f"Bot online como {self.user}")

    async def on_application_command_error(self, ctx, error):
        if isinstance(error, discord.ApplicationCommandError):
            await ctx.respond(f"❌ {str(error)}", ephemeral=True)
        else:
            log.error(f"Erro inesperado: {error}")
            await ctx.respond("❌ Ocorreu um erro inesperado.", ephemeral=True)


def main():
    bot = CapybaraBot()
    extensions = ["bot.cogs.chat", "bot.cogs.config_cog", "bot.cogs.generate"]
    for ext in extensions:
        bot.load_extension(ext)
        log.info(f"Extensao carregada: {ext}")
    bot.run(settings.discord_token)


if __name__ == "__main__":
    main()

import discord
from discord.ext import commands
from utils.logging import get_logger

log = get_logger("bot.cogs.config")


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="config", description="Configurações do bot")
    async def config(self, ctx: discord.ApplicationContext):
        await ctx.respond("⚙️ Comando /config em construção...", ephemeral=True)


def setup(bot):
    bot.add_cog(ConfigCog(bot))

import discord
from discord.ext import commands
from bot.middleware.auth import require_authorized
from bot.middleware.rate_limit import rate_limit_check
from utils.logging import get_logger

log = get_logger("bot.cogs.generate")


class GenerateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="msg", description="Gera uma resposta de texto")
    @require_authorized
    @rate_limit_check("llm")
    async def msg(self, ctx: discord.ApplicationContext, prompt: str):
        await ctx.respond("🤖 Comando /msg em construção...", ephemeral=True)

    @discord.slash_command(name="imagem", description="Gera uma imagem")
    @require_authorized
    @rate_limit_check("imagem")
    async def imagem(self, ctx: discord.ApplicationContext, prompt: str):
        await ctx.respond("🎨 Comando /imagem em construção...", ephemeral=True)

    @discord.slash_command(name="audio", description="Gera um áudio")
    @require_authorized
    @rate_limit_check("audio")
    async def audio(self, ctx: discord.ApplicationContext, prompt: str):
        await ctx.respond("🎵 Comando /audio em construção...", ephemeral=True)


def setup(bot):
    bot.add_cog(GenerateCog(bot))

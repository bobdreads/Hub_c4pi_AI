import discord
from discord.ext import commands
from utils.logging import get_logger

log = get_logger("bot.cogs.chat")


class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="chat", description="Gerencia conversas")
    async def chat(self, ctx: discord.ApplicationContext):
        await ctx.respond("💬 Comando /chat em construção...", ephemeral=True)


def setup(bot):
    bot.add_cog(ChatCog(bot))

import discord
from discord.ext import commands
from bot.middleware.auth import require_authorized
from bot.middleware.rate_limit import rate_limit_check
from adapters.base import GenerationRequest
from adapters.factory import AdapterFactory
from services.generation import generation_service
from utils.logging import get_logger
from services.memory import memory_service


log = get_logger("bot.cogs.generate")


class GenerateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="msg", description="Gera uma resposta de texto")
    @require_authorized
    @rate_limit_check("llm")
    async def msg(
        self,
        ctx: discord.ApplicationContext,
        prompt: str,
        modelo: str = "openai/gpt-5.4-mini"
    ):
        await ctx.defer(ephemeral=False)

        # Monta request com histórico do banco
        req, user_id, chat_id = await memory_service.build_request_with_history(
            prompt=prompt,
            model=modelo,
            discord_id=str(ctx.author.id),
            username=ctx.author.display_name,
            channel_id=str(ctx.channel_id),
        )

        result = await generation_service.run(req)

        # Salva mensagens no banco
        await memory_service.save(chat_id, user_id, prompt, result)

        await ctx.followup.send(f"**{ctx.author.display_name}:** {prompt}\n\n{result.content}")

    @discord.slash_command(name="imagem", description="Gera uma imagem")
    @require_authorized
    @rate_limit_check("imagem")
    async def imagem(self, ctx: discord.ApplicationContext, prompt: str):
        await ctx.defer(ephemeral=False)
        result = await generation_service.run_image(prompt)
        await ctx.followup.send(f"🎨 **{prompt}**\n{result.media_url}")

    @discord.slash_command(name="audio", description="Gera um áudio")
    @require_authorized
    @rate_limit_check("audio")
    async def audio(self, ctx: discord.ApplicationContext, prompt: str):
        await ctx.respond("🎵 Geração de áudio em breve!", ephemeral=True)

    # ──── ADICIONA AQUI ────
    @discord.slash_command(name="modelos", description="Lista todos os modelos LLM disponíveis")
    async def modelos(self, ctx: discord.ApplicationContext):
        catalog = AdapterFactory.list_models()

        embed = discord.Embed(
            title="🤖 Modelos LLM Disponíveis",
            description="Use o ID do modelo no comando `/msg`",
            color=0x01696f
        )

        for provider, models in catalog.items():
            value = "\n".join([f"`{mid}` — {desc}" for mid, desc in models])
            embed.add_field(name=f"**{provider}**", value=value, inline=False)

        embed.set_footer(
            text="Padrão: openai/gpt-5.4-mini | Exemplo: /msg modelo:xai/grok-4 prompt:...")
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(GenerateCog(bot))

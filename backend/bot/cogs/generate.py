import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from services.generation import GenerationService
from schemas.params import LLMParams, PARAM_PRESETS
from utils.file_reader import process_attachment
from utils.logging import get_logger

from database.queries.users import get_user_params, get_api_key, get_or_create_user
from database.queries.chats import get_or_create_chat
from database.pool import get_pool

log = get_logger("bot.cogs.generate")


class GenerateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="msg", description="Envia uma mensagem para o LLM")
    async def msg(
        self,
        ctx: discord.ApplicationContext,
        prompt: Option(str, "Sua mensagem ou pergunta"),
        arquivo: Option(
            discord.Attachment, "Imagem, PDF, TXT ou CSV para enviar junto", required=False) = None,
        modelo: Option(
            str, "Modelo a usar (opcional, sobrescreve o configurado)", required=False) = None,
        preset: Option(
            str, "Preset de parâmetros: preciso | normal | criativo | codigo | resumo", required=False) = None,
        temp: Option(float, "Temperatura 0.0–2.0 (opcional)",
                     required=False) = None,
    ):
        await ctx.defer()

        user_discord_id = str(ctx.author.id)
        guild_id = str(ctx.guild_id)

        pool = await get_pool()

        # 1. Fazemos a tradução! Pegamos o seu UUID interno do banco de dados
        user = await get_or_create_user(pool, user_discord_id, ctx.author.name)
        user_uuid = str(user["id"])

        try:
            # Esses continuam precisando do Discord ID (estão configurados assim no banco)
            api_key = await get_api_key(pool, user_discord_id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await ctx.respond(f"❌ Você precisa configurar sua API Key primeiro com `/config api_key`.", ephemeral=True)
            return

        params = await get_user_params(pool, user_discord_id) or LLMParams()

        if preset and preset in PARAM_PRESETS:
            params = PARAM_PRESETS[preset].model_copy()

        if modelo:
            params.model = modelo
        if temp is not None:
            params.temperature = temp

        files = []
        if arquivo:
            try:
                data = await arquivo.read()
                af = await process_attachment(arquivo.filename, data, arquivo.content_type)
                files.append(af)
            except ValueError as e:
                await ctx.respond(f"❌ {e}", ephemeral=True)
                return

        # 2. AQUI ESTÁ A CORREÇÃO! Passamos o user_uuid para a criação do chat
        chat_id = await get_or_create_chat(pool, user_uuid, guild_id,
                                           str(ctx.channel_id), params.model)

        svc = GenerationService(pool, None)

        # O user_uuid também segue para a geração de memória
        result = await svc.run(prompt, user_uuid, chat_id, params, api_key=api_key, files=files)

        if not result.success:
            await ctx.respond(f"❌ Erro: {result.error}", ephemeral=True)
            return

        resposta = result.text
        footer = (f"-# 🤖 `{result.model}` · "
                  f"{result.total_tokens} tokens · "
                  f"{result.latency_ms:.0f}ms")

        if len(resposta) + len(footer) <= 1900:
            await ctx.respond(resposta + "\n" + footer)
        else:
            chunks = [resposta[i:i+1900]
                      for i in range(0, len(resposta), 1900)]
            for i, chunk in enumerate(chunks):
                suffix = ("\n" + footer) if i == len(chunks) - 1 else ""
                if i == 0:
                    await ctx.respond(chunk + suffix)
                else:
                    await ctx.send(chunk + suffix)

    @slash_command(name="modelos", description="Lista todos os modelos disponíveis")
    async def modelos(self, ctx: discord.ApplicationContext):
        from adapters.factory import AdapterFactory
        catalog = AdapterFactory.list_models()

        embed = discord.Embed(
            title="🤖 Modelos LLM Disponíveis",
            description="Use o ID no parâmetro `modelo` do `/msg`",
            color=0x01696f
        )
        for provider, models in catalog.items():
            value = "\n".join([f"`{mid}` — {desc}" for mid, desc in models])
            embed.add_field(name=f"**{provider}**", value=value, inline=False)

        embed.set_footer(
            text="Exemplo: /msg prompt:Olá modelo:anthropic/claude-sonnet-4.6")
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(GenerateCog(bot))

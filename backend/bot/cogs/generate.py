import discord
from discord import app_commands
from discord.ext import commands

from services.generation import GenerationService
from schemas.params import LLMParams, PARAM_PRESETS
from utils.file_reader import process_attachment
from utils.logging import get_logger
from database.queries.users import get_user_params, get_or_create_chat


log = get_logger("bot.cogs.generate")


class GenerateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="msg", description="Envia uma mensagem para o LLM")
    @app_commands.describe(
        prompt="Sua mensagem ou pergunta",
        arquivo="Imagem, PDF, TXT ou CSV para enviar junto",
        modelo="Modelo a usar (opcional, sobrescreve o configurado)",
        preset="Preset de parâmetros: preciso | normal | criativo | codigo | resumo",
        temp="Temperatura 0.0–2.0 (opcional)",
    )
    async def msg(
        self,
        interaction: discord.Interaction,
        prompt:   str,
        arquivo:  discord.Attachment = None,
        modelo:   str = None,
        preset:   str = None,
        temp:     float = None,
    ):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)

        # Carregar parâmetros salvos do usuário
        params = await get_user_params(self.bot.db, user_id) or LLMParams()

        # Aplicar preset se informado
        if preset and preset in PARAM_PRESETS:
            params = PARAM_PRESETS[preset].model_copy()

        # Sobrescrever modelo e temp se informados no comando
        if modelo:
            params.model = modelo
        if temp is not None:
            params.temperature = temp

        # Processar arquivo anexado
        files = []
        if arquivo:
            try:
                data = await arquivo.read()
                af = await process_attachment(arquivo.filename, data, arquivo.content_type)
                files.append(af)
            except ValueError as e:
                await interaction.followup.send(f"❌ {e}", ephemeral=True)
                return

        # Pegar ou criar chat_id para este canal
        chat_id = await get_or_create_chat(self.bot.db, user_id, guild_id,
                                           str(interaction.channel_id), params.model)

        # Rodar geração
        svc = GenerationService(self.bot.db, self.bot.redis)
        result = await svc.run(prompt, user_id, chat_id, params, files)

        if not result.success:
            await interaction.followup.send(f"❌ Erro: {result.error}", ephemeral=True)
            return

        # Formatar resposta
        resposta = result.text
        footer = (f"-# 🤖 `{result.model}` · "
                  f"{result.total_tokens} tokens · "
                  f"{result.latency_ms:.0f}ms")

        # Discord tem limite de 2000 chars — dividir se necessário
        if len(resposta) + len(footer) <= 1900:
            await interaction.followup.send(resposta + "\n" + footer)
        else:
            # Manda em partes
            chunks = [resposta[i:i+1900]
                      for i in range(0, len(resposta), 1900)]
            for i, chunk in enumerate(chunks):
                suffix = ("\n" + footer) if i == len(chunks) - 1 else ""
                await interaction.followup.send(chunk + suffix)

    @app_commands.command(name="modelos", description="Lista todos os modelos disponíveis")
    async def modelos(self, interaction: discord.Interaction):
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
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(GenerateCog(bot))

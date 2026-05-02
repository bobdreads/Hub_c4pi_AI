import discord
from discord import app_commands
from discord.ext import commands
from schemas.params import LLMParams, PARAM_PRESETS
from database.queries.users import save_user_params
from utils.logging import get_logger

log = get_logger("cogs.config")


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    config_group = app_commands.Group(
        name="config", description="Configurações do bot")

    @config_group.command(name="llm", description="Configura parâmetros padrão do LLM")
    @app_commands.describe(
        modelo="Modelo padrão a usar",
        temperatura="Criatividade 0.0–2.0 (padrão: 0.7)",
        max_tokens="Máximo de tokens na resposta (padrão: 2048)",
        preset="Aplicar preset: preciso | normal | criativo | codigo | resumo",
        system="Instrução de sistema personalizada",
        contexto="Quantas mensagens anteriores incluir (padrão: 20)",
    )
    async def config_llm(
        self,
        interaction: discord.Interaction,
        modelo:      str = None,
        temperatura: float = None,
        max_tokens:  int = None,
        preset:      str = None,
        system:      str = None,
        contexto:    int = None,
    ):
        user_id = str(interaction.user.id)

        # Carregar config atual
        from database.queries.users import get_user_params
        params = await get_user_params(self.bot.db, user_id) or LLMParams()

        # Aplicar preset primeiro (base)
        if preset:
            if preset not in PARAM_PRESETS:
                lista = ", ".join(PARAM_PRESETS.keys())
                await interaction.response.send_message(
                    f"❌ Preset `{preset}` não existe. Disponíveis: `{lista}`",
                    ephemeral=True
                )
                return
            params = PARAM_PRESETS[preset].model_copy()

        # Sobrescrever campos individuais
        if modelo:
            params.model = modelo
        if temperatura:
            params.temperature = temperatura
        if max_tokens:
            params.max_tokens = max_tokens
        if system:
            params.system_prompt = system
        if contexto:
            params.context_limit = contexto

        # Salvar no banco
        await save_user_params(self.bot.db, user_id, params)

        embed = discord.Embed(
            title="✅ Configurações salvas",
            color=0x01696f
        )
        embed.add_field(name="Modelo",
                        value=f"`{params.model}`",          inline=True)
        embed.add_field(name="Temperatura",
                        value=f"`{params.temperature}`",    inline=True)
        embed.add_field(name="Max Tokens",
                        value=f"`{params.max_tokens}`",     inline=True)
        embed.add_field(name="Contexto",
                        value=f"`{params.context_limit}` msgs", inline=True)
        if params.system_prompt:
            embed.add_field(name="System Prompt",
                            value=f"```{params.system_prompt[:200]}```",
                            inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="ver", description="Mostra suas configurações atuais")
    async def config_ver(self, interaction: discord.Interaction):
        from database.queries.users import get_user_params
        user_id = str(interaction.user.id)
        params = await get_user_params(self.bot.db, user_id) or LLMParams()

        embed = discord.Embed(title="⚙️ Suas Configurações", color=0x01696f)
        embed.add_field(name="Modelo",
                        value=f"`{params.model}`",       inline=True)
        embed.add_field(name="Temperatura",
                        value=f"`{params.temperature}`", inline=True)
        embed.add_field(name="Max Tokens",
                        value=f"`{params.max_tokens}`",  inline=True)
        embed.add_field(name="Top P",
                        value=f"`{params.top_p}`",       inline=True)
        embed.add_field(name="Contexto",
                        value=f"`{params.context_limit}` msgs", inline=True)
        if params.system_prompt:
            embed.add_field(name="System Prompt",
                            value=f"```{params.system_prompt[:300]}```",
                            inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @config_group.command(name="reset", description="Reseta configurações para o padrão")
    async def config_reset(self, interaction: discord.Interaction):
        from database.queries.users import save_user_params
        user_id = str(interaction.user.id)
        await save_user_params(self.bot.db, user_id, LLMParams())
        await interaction.response.send_message(
            "✅ Configurações resetadas para o padrão.", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(ConfigCog(bot))

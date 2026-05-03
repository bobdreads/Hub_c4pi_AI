import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from schemas.params import LLMParams, PARAM_PRESETS
from database.queries.users import save_user_params, get_user_params, get_or_create_user
from database.pool import get_pool  # <-- Importamos o pool de conexão real
from utils.logging import get_logger

log = get_logger("cogs.config")


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Criação do grupo de comandos no Pycord
    config_group = SlashCommandGroup(
        name="config", description="Configurações do bot")

    @config_group.command(name="llm", description="Configura parâmetros padrão do LLM")
    async def config_llm(
        self,
        ctx: discord.ApplicationContext,
        modelo: Option(str, "Modelo padrão a usar", required=False) = None,
        temperatura: Option(
            float, "Criatividade 0.0–2.0 (padrão: 0.7)", required=False) = None,
        max_tokens: Option(
            int, "Máximo de tokens na resposta (padrão: 2048)", required=False) = None,
        preset: Option(
            str, "Aplicar preset: preciso | normal | criativo | codigo | resumo", required=False) = None,
        system: Option(str, "Instrução de sistema personalizada",
                       required=False) = None,
        contexto: Option(
            int, "Quantas mensagens anteriores incluir (padrão: 20)", required=False) = None,
    ):
        user_id = str(ctx.author.id)
        pool = await get_pool()  # <-- Usando o pool

        # Carregar config atual
        params = await get_user_params(pool, user_id) or LLMParams()

        # Aplicar preset primeiro (base)
        if preset:
            if preset not in PARAM_PRESETS:
                lista = ", ".join(PARAM_PRESETS.keys())
                await ctx.respond(
                    f"❌ Preset `{preset}` não existe. Disponíveis: `{lista}`",
                    ephemeral=True
                )
                return
            params = PARAM_PRESETS[preset].model_copy()

        # Sobrescrever campos individuais
        if modelo:
            params.model = modelo
        if temperatura is not None:
            params.temperature = temperatura
        if max_tokens:
            params.max_tokens = max_tokens
        if system:
            params.system_prompt = system
        if contexto is not None:
            params.context_limit = contexto

        # Salvar no banco
        await save_user_params(pool, user_id, params)

        embed = discord.Embed(
            title="✅ Configurações salvas",
            color=0x01696f
        )
        embed.add_field(name="Modelo", value=f"`{params.model}`", inline=True)
        embed.add_field(name="Temperatura",
                        value=f"`{params.temperature}`", inline=True)
        embed.add_field(name="Max Tokens",
                        value=f"`{params.max_tokens}`", inline=True)
        embed.add_field(name="Contexto",
                        value=f"`{params.context_limit}` msgs", inline=True)
        if params.system_prompt:
            embed.add_field(name="System Prompt",
                            value=f"```{params.system_prompt[:200]}```",
                            inline=False)

        await ctx.respond(embed=embed, ephemeral=True)

    @config_group.command(name="ver", description="Mostra suas configurações atuais")
    async def config_ver(self, ctx: discord.ApplicationContext):
        user_id = str(ctx.author.id)
        pool = await get_pool()  # <-- Usando o pool
        params = await get_user_params(pool, user_id) or LLMParams()

        embed = discord.Embed(title="⚙️ Suas Configurações", color=0x01696f)
        embed.add_field(name="Modelo", value=f"`{params.model}`", inline=True)
        embed.add_field(name="Temperatura",
                        value=f"`{params.temperature}`", inline=True)
        embed.add_field(name="Max Tokens",
                        value=f"`{params.max_tokens}`", inline=True)
        embed.add_field(name="Top P", value=f"`{params.top_p}`", inline=True)
        embed.add_field(name="Contexto",
                        value=f"`{params.context_limit}` msgs", inline=True)
        if params.system_prompt:
            embed.add_field(name="System Prompt",
                            value=f"```{params.system_prompt[:300]}```",
                            inline=False)

        await ctx.respond(embed=embed, ephemeral=True)

    @config_group.command(name="reset", description="Reseta configurações para o padrão")
    async def config_reset(self, ctx: discord.ApplicationContext):
        user_id = str(ctx.author.id)
        pool = await get_pool()  # <-- Usando o pool
        await save_user_params(pool, user_id, LLMParams())
        await ctx.respond("✅ Configurações resetadas para o padrão.", ephemeral=True)

    @config_group.command(name="api_key", description="Salva sua API Key no banco (Criptografada)")
    async def config_apikey(self, ctx: discord.ApplicationContext, key: discord.Option(str, "Sua chave de API")):
        await ctx.defer(ephemeral=True)

        try:
            from utils.crypto import encrypt

            user_id = str(ctx.author.id)
            username = ctx.author.name
            pool = await get_pool()  # <-- Usando o pool

            # Garante que o usuário existe no banco ANTES de atualizar
            await get_or_create_user(pool, user_id, username)

            # Criptografa a chave usando o seu crypto.py
            encrypted_key = encrypt(key)

            # Atualiza a chave do usuário no banco
            await pool.execute(
                "UPDATE users SET api_key_enc = $1 WHERE discord_id = $2",
                encrypted_key, user_id
            )

            await ctx.respond("✅ Sua API Key foi salva e criptografada com segurança!", ephemeral=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await ctx.respond(f"❌ Erro ao salvar chave: {str(e)}", ephemeral=True)


def setup(bot):
    bot.add_cog(ConfigCog(bot))

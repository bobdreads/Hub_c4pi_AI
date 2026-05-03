import discord
from discord.ext import commands
from services.memory import memory_service
from database.queries.users import get_or_create_user
from database.queries.chats import get_or_create_chat

# Adicionamos a importação correta do banco de dados
from database.pool import get_pool


class MemoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    memory = discord.SlashCommandGroup(
        "memoria", "Gerenciar memória semântica da IA")

    @memory.command(name="buscar", description="Busca lembranças no banco de dados da IA")
    async def memory_search(self, ctx: discord.ApplicationContext, query: discord.Option(str, "O que você quer buscar na memória?")):
        await ctx.defer(ephemeral=True)

        try:
            # Pegamos a conexão com o banco
            pool = await get_pool()

            # 1. Traduz o Discord ID para o UUID interno do usuário
            user = await get_or_create_user(pool, str(ctx.author.id), ctx.author.name)
            user_uuid = str(user["id"])

            # 2. Faz a busca usando o UUID correto
            memories = await memory_service.search_semantic(user_uuid, query, api_key=None, limit=5)

            if not memories:
                await ctx.respond("🧠 Nenhuma memória relevante encontrada para essa busca.", ephemeral=True)
                return

            embed = discord.Embed(
                title="🧠 Memórias Encontradas", color=discord.Color.blurple())
            for i, m in enumerate(memories):
                content = m['content'][:1000] + \
                    "..." if len(m['content']) > 1000 else m['content']
                embed.add_field(
                    name=f"Resultado {i+1} (Relevância: {m['similarity']:.2f})",
                    value=content,
                    inline=False
                )

            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            # Imprime o erro no console também para facilitar a nossa vida se der problema
            import traceback
            traceback.print_exc()
            await ctx.respond(f"❌ Erro ao buscar memória: {str(e)}", ephemeral=True)

    @memory.command(name="salvar", description="Salva um texto manualmente na memória da IA")
    async def memory_save(self, ctx: discord.ApplicationContext, texto: discord.Option(str, "Texto que a IA deve lembrar no futuro")):
        await ctx.defer(ephemeral=True)

        try:
            # Pegamos a conexão com o banco
            pool = await get_pool()

            # 1. Traduz os IDs do Discord para UUIDs do usuário e do chat
            user = await get_or_create_user(pool, str(ctx.author.id), ctx.author.name)
            user_uuid = str(user["id"])

            chat = await get_or_create_chat(pool, user_uuid, str(ctx.channel.id), "default", "")
            chat_uuid = str(chat["id"])

            # 2. Salva a memória passando os UUIDs corretos
            await memory_service.save_semantic(user_uuid, chat_uuid, texto, api_key=None, metadata={"origem": "manual"})

            await ctx.respond("✅ Conhecimento salvo na memória com sucesso!", ephemeral=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            await ctx.respond(f"❌ Erro ao salvar memória: {str(e)}", ephemeral=True)


def setup(bot):
    bot.add_cog(MemoryCog(bot))

from discord.ext import commands
from discord import app_commands
import discord

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, ext):
        try:
            await ctx.bot.reload_extension(f"cogs.{ext}")
            await ctx.send(f"🔄 {ext} recargado")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, ext):
        try:
            await ctx.bot.load_extension(f"cogs.{ext}")
            await ctx.send(f"✅ {ext} cargado")
        except Exception as e:
            await ctx.send(f"Error: {e}")
            
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, ext):
        try:
            await ctx.bot.unload_extension(f"cogs.{ext}")
            await ctx.send(f"⏬ {ext} descargado")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.hybrid_command(
        name="sync",
        description="🔄 Sincroniza los slash commands con Discord (owner only)",
    )
    @commands.is_owner()
    @app_commands.describe(
        modo="Usa 'guild' para solo este servidor, 'global' para todos, 'clean' para limpiar duplicados",
    )
    @app_commands.choices(modo=[
        app_commands.Choice(name="🌍 Global (lento, 1h)", value="global"),
        app_commands.Choice(name="🏠 Este servidor (rápido)", value="guild"),
        app_commands.Choice(name="🧹 Limpiar + resincronizar", value="clean"),
    ])
    async def sync(self, ctx: commands.Context, modo: str = "guild"):
        """Sincronizar comandos slash con Discord.

        &sync guild → solo este servidor (rápido)
        &sync global → global (lento, hasta 1h)
        &sync clean → limpia duplicados y resincroniza
        """
        if modo == "global":
            await ctx.send("⏳ Sincronizando globalmente... (puede tardar hasta 1h en propagarse)")
            synced = await self.bot.tree.sync()
            await ctx.send(f"✅ **{len(synced)}** comandos sincronizados globalmente.")

        elif modo == "clean":
            await ctx.send("🧹 Limpiando comandos duplicados del servidor...")
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
            # Ahora copiar de nuevo desde global
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ **{len(synced)}** comandos limpios y sincronizados en **{ctx.guild.name}**")

        else:  # guild
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ **{len(synced)}** comandos sincronizados en **{ctx.guild.name}**")

    @commands.command()
    @commands.is_owner()
    async def serverlist(self, ctx):
        """Lista los servidores donde está el bot"""
        servers = self.bot.guilds
        if not servers:
            await ctx.send("❌ No estoy en ningún servidor")
            return
        
        msg = "📋 **Servidores:**\n\n"
        for i, guild in enumerate(servers, 1):
            msg += f"{i}. **{guild.name}** (ID: {guild.id}) — {guild.member_count} miembros\n"
        
        if len(msg) > 2000:
            msg = msg[:1997] + "..."
        await ctx.send(msg)

    @commands.command()
    @commands.is_owner()
    async def botstatus(self, ctx, *, estado: str):
        """Cambia el estado del bot"""
        await self.bot.change_presence(activity=discord.Game(name=estado))
        await ctx.send(f"✅ Estado cambiado a: **Jugando {estado}**")

async def setup(bot):
    await bot.add_cog(Admin(bot))

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
        especifico="Usa '.' para sincronizar solo en este servidor (rápido)",
    )
    async def sync(self, ctx: commands.Context, especifico: str = None):
        """Sincronizar comandos slash con Discord.
        
        Uso: &sync → global (lento, hasta 1h)
              &sync . → solo este servidor (instantáneo)
        """
        if especifico == ".":
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"✅ **{len(synced)}** comandos sincronizados en **{ctx.guild.name}**")
        else:
            await ctx.send("⏳ Sincronizando globalmente... (esto puede tardar hasta 1 hora en propagarse)")
            synced = await self.bot.tree.sync()
            await ctx.send(f"✅ **{len(synced)}** comandos sincronizados globalmente.")

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

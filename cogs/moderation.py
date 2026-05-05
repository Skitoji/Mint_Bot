from discord.ext import commands
import discord
import json
import os
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns_file = "data/warns.json"
        self.load_warns()
    
    def load_warns(self):
        # Asegurar que la carpeta data existe
        if not os.path.exists("data"):
            os.makedirs("data")
        if os.path.exists(self.warns_file):
            with open(self.warns_file) as f:
                self.warns = json.load(f)
        else:
            self.warns = {}
    
    def save_warns(self):
        with open(self.warns_file, "w") as f:
            json.dump(self.warns, f, indent=2)
    
    @commands.hybrid_command(name="warn", description="Advierte a un usuario (se le envía DM)")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str = "Sin razón"):
        await ctx.defer()
        try:
            if user.top_role >= ctx.author.top_role:
                await ctx.send("❌ No puedes advertir a este usuario", ephemeral=True)
                return
            
            user_id = str(user.id)
            if user_id not in self.warns:
                self.warns[user_id] = []
            
            self.warns[user_id].append({
                'reason': reason,
                'by': ctx.author.name
            })
            self.save_warns()
            
            warn_count = len(self.warns[user_id])
            embed = discord.Embed(
                title="⚠️ Usuario Advertido",
                description=f"{user.mention} ha sido advertido\n\n**Razón:** {reason}",
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"Advertencias: {warn_count}/3")
            await ctx.send(embed=embed)
            
            # DM con GIF
            WARN_GIF = "https://tenor.com/hvg3RW8UTyM.gif"
            try:
                await user.send(
                    f"⚠️ Has sido advertido en **{ctx.guild.name}**\n"
                    f"**Razón:** {reason}\n"
                    f"**Advertencias:** {warn_count}/3\n\n"
                    f"{WARN_GIF}"
                )
            except:
                pass
            
            if warn_count >= 3:
                await ctx.send(f"❌ {user.mention} ha sido expulsado por acumular 3 advertencias")
                await user.kick(reason="3 advertencias acumuladas")
                del self.warns[user_id]
                self.save_warns()
        except Exception as e:
            await ctx.send(f"❌ Error interno: {e}", ephemeral=True)
            print(f"Error en warn: {e}")
    
    @commands.hybrid_command(name="mute", description="Silencia a un usuario por X segundos")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, user: discord.Member, duration: int, *, reason: str = "Sin razón"):
        await ctx.defer()
        try:
            if user.top_role >= ctx.author.top_role:
                await ctx.send("❌ No puedes silenciar a este usuario", ephemeral=True)
                return
            
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not muted_role:
                muted_role = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False)
            
            await user.add_roles(muted_role)
            
            try:
                await user.send(f"🔇 Has sido silenciado en **{ctx.guild.name}** por {duration} segundos.\n**Razón:** {reason}")
            except:
                pass
            
            embed = discord.Embed(
                title="🔇 Usuario Silenciado",
                description=f"{user.mention} ha sido silenciado\n**Razón:** {reason}",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Duración: {duration}s")
            await ctx.send(embed=embed)
            
            await asyncio.sleep(duration)
            await user.remove_roles(muted_role)
            await ctx.send(f"🔊 {user.mention} ha sido desilenciado")
        except Exception as e:
            await ctx.send(f"❌ Error interno: {e}", ephemeral=True)
            print(f"Error en mute: {e}")
    
    @commands.hybrid_command(name="kick", description="Expulsa a un usuario del servidor")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = "Sin razón"):
        await ctx.defer()
        try:
            if user.top_role >= ctx.author.top_role:
                await ctx.send("❌ No puedes expulsar a este usuario", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="👢 Usuario Expulsado",
                description=f"{user.mention} ha sido expulsado\n**Razón:** {reason}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            await user.kick(reason=reason)
            
            try:
                await user.send(f"👢 Has sido expulsado de {ctx.guild.name}\n**Razón:** {reason}")
            except:
                pass
        except Exception as e:
            await ctx.send(f"❌ Error interno: {e}", ephemeral=True)
            print(f"Error en kick: {e}")
    
    @commands.hybrid_command(name="ban", description="Banea a un usuario del servidor")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str = "Sin razón"):
        await ctx.defer()
        try:
            if user.top_role >= ctx.author.top_role:
                await ctx.send("❌ No puedes banear a este usuario", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🔨 Usuario Baneado",
                description=f"{user.mention} ha sido baneado\n**Razón:** {reason}",
                color=discord.Color.dark_red()
            )
            await ctx.send(embed=embed)
            await ctx.guild.ban(user, reason=reason)
            
            try:
                await user.send(f"🔨 Has sido baneado de {ctx.guild.name}\n**Razón:** {reason}")
            except:
                pass
        except Exception as e:
            await ctx.send(f"❌ Error interno: {e}", ephemeral=True)
            print(f"Error en ban: {e}")
    
    @commands.hybrid_command(name="unban", description="Desbanea a un usuario por su ID")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = "Sin razón"):
        await ctx.defer()
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"✅ {user.mention} ha sido desbaneado")
        except:
            await ctx.send("❌ Usuario no encontrado", ephemeral=True)
    
    @commands.hybrid_command(name="warns", description="Muestra las advertencias de un usuario")
    async def warns(self, ctx, user: discord.Member = None):
        await ctx.defer()
        try:
            if user is None:
                user = ctx.author
            
            user_id = str(user.id)
            warn_list = self.warns.get(user_id, [])
            
            if not warn_list:
                await ctx.send(f"{user.mention} no tiene advertencias", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"⚠️ Advertencias de {user.name}",
                color=discord.Color.orange()
            )
            for i, warn in enumerate(warn_list, 1):
                embed.add_field(
                    name=f"Advertencia #{i}",
                    value=f"**Razón:** {warn['reason']}\n**Por:** {warn['by']}",
                    inline=False
                )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error interno: {e}", ephemeral=True)
            print(f"Error en warns: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
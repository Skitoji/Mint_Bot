from discord.ext import commands
from discord import app_commands
import discord
from utils import ui
from typing import Literal

class Leaderboards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="topglobal", description="Muestra los mejores usuarios en diferentes categorías (coins, xp, marriage)")
    @app_commands.describe(category="Categoría del ranking (coins/xp/marriage)")
    async def topglobal(self, ctx, category: Literal["coins", "xp", "marriage"] = "coins"):
        await ctx.defer()  # ← Evita timeouts
        if category == "coins":
            await self._show_coins_lb(ctx)
        elif category == "xp":
            await self._show_xp_lb(ctx)
        elif category == "marriage":
            await self._show_marriage_lb(ctx)
        else:
            await ctx.send(embed=ui.error_embed("Categoría inválida: coins, xp, marriage"), ephemeral=True)
    
    async def _get_balances(self, economy_cog):
        """Intenta obtener el diccionario de balances desde el cog Economy, sea cual sea su nombre interno"""
        # Posibles nombres de atributo donde se guardan los balances
        posibles = ['balances', 'economy', 'balance', 'coins', 'money']
        for attr in posibles:
            if hasattr(economy_cog, attr):
                data = getattr(economy_cog, attr)
                if isinstance(data, dict):
                    return data
        # Si no encuentra ninguno, intenta acceder a un método (si existe)
        if hasattr(economy_cog, 'get_balance'):
            # No podemos obtener el diccionario completo fácilmente, así que intentamos con todos los usuarios del servidor
            # (truco lento) – mejor pedir ayuda
            return None
        return None

    async def _show_coins_lb(self, ctx):
        """Leaderboard de coins"""
        economy = self.bot.get_cog('Economy')
        if not economy:
            await ctx.send(embed=ui.error_embed("Economy cog no encontrado"), ephemeral=True)
            return
        
        balances = await self._get_balances(economy)
        if not balances:
            await ctx.send(embed=ui.error_embed("No se pudieron obtener los datos de economía. Contacta al administrador."), ephemeral=True)
            return
        
        sorted_users = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:10]
        
        embed = ui.simple_embed(
            title="💰 Leaderboard de Coins",
            description="Top 10 usuarios más ricos",
            color=discord.Color.gold()
        )
        
        for i, (user_id, balance) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"#{i}"
                embed.add_field(
                    name=f"{medal} {user.name}",
                    value=f"💰 **{balance}** coins",
                    inline=False
                )
            except:
                pass
        
        await ctx.send(embed=embed)
    
    async def _get_xp_data(self, xp_cog):
        """Intenta obtener el diccionario de XP desde el cog XP"""
        posibles = ['xp_data', 'xp', 'levels', 'user_xp']
        for attr in posibles:
            if hasattr(xp_cog, attr):
                data = getattr(xp_cog, attr)
                if isinstance(data, dict):
                    return data
        return None

    async def _show_xp_lb(self, ctx):
        """Leaderboard de XP"""
        xp_cog = self.bot.get_cog('XP')
        if not xp_cog:
            await ctx.send(embed=ui.error_embed("XP cog no encontrado"), ephemeral=True)
            return
        
        xp_data = await self._get_xp_data(xp_cog)
        if not xp_data:
            await ctx.send(embed=ui.error_embed("No se pudieron obtener los datos de XP"), ephemeral=True)
            return
        
        # Ordenar por nivel y luego por XP acumulada
        sorted_users = sorted(
            xp_data.items(),
            key=lambda x: (x[1].get('level', 0), x[1].get('xp', 0)),
            reverse=True
        )[:10]
        
        embed = ui.simple_embed(
            title="⭐ Leaderboard de XP",
            description="Top 10 usuarios más experimentados",
            color=discord.Color.purple()
        )
        
        for i, (user_id, data) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"#{i}"
                level = data.get('level', 0)
                xp = data.get('xp', 0)
                embed.add_field(
                    name=f"{medal} {user.name}",
                    value=f"⭐ Nivel {level} ({xp} XP)",
                    inline=False
                )
            except Exception as e:
                print(f"Error mostrando usuario en XP leaderboard: {e}")
        
        await ctx.send(embed=embed)
    
    async def _show_marriage_lb(self, ctx):
        """Leaderboard de parejas"""
        profile = self.bot.get_cog('Profile')
        if not profile:
            await ctx.send(embed=ui.error_embed("Profile cog no encontrado"), ephemeral=True)
            return
        
        # Intentar acceder a profiles
        profiles = None
        if hasattr(profile, 'profiles'):
            profiles = profile.profiles
        elif hasattr(profile, 'data'):
            profiles = profile.data
        else:
            await ctx.send(embed=ui.error_embed("No se pudieron obtener los datos de perfiles"), ephemeral=True)
            return
        
        couples = []
        seen = set()
        
        for user_id, data in profiles.items():
            spouse_id = data.get('married_to')
            if spouse_id and user_id not in seen and spouse_id not in seen:
                couples.append((user_id, spouse_id))
                seen.add(user_id)
                seen.add(spouse_id)
        
        if not couples:
            await ctx.send(embed=ui.info_embed("Parejas", "No hay parejas registradas"), ephemeral=True)
            return
        
        embed = ui.simple_embed(
            title="💑 Parejas Registradas",
            description=f"Total de parejas: {len(couples)}",
            color=discord.Color.pink()
        )
        
        for i, (user1_id, user2_id) in enumerate(couples[:10], 1):
            try:
                user1 = await self.bot.fetch_user(int(user1_id))
                user2 = await self.bot.fetch_user(int(user2_id))
                embed.add_field(
                    name=f"💒 Pareja #{i}",
                    value=f"{user1.name} ❤️ {user2.name}",
                    inline=False
                )
            except:
                pass
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboards(bot))
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random


class Interaction(commands.Cog):
    """Comandos de interacción social con GIFs animados"""

    def __init__(self, bot):
        self.bot = bot
        self.api_base = "https://nekos.best/api/v2"

    async def fetch_gif(self, action: str) -> str | None:
        """Obtiene un GIF desde la API de nekos.best"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/{action}", timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("results", [])
                        if results:
                            return results[0]["url"]
        except Exception:
            pass
        return None

    async def _send_action(
        self,
        ctx: commands.Context,
        action: str,
        verb: str,
        *,
        target: discord.Member | None = None,
        emoji: str = "",
    ) -> None:
        """Método base para enviar interacciones"""
        gif_url = await self.fetch_gif(action)

        embed = discord.Embed(color=discord.Color.blurple())

        if target:
            embed.description = f"**{ctx.author.mention}** {verb} **{target.mention}** {emoji}"
        else:
            embed.description = f"**{ctx.author.mention}** {verb} {emoji}"

        if gif_url:
            embed.set_image(url=gif_url)
        else:
            embed.set_footer(text="No se pudo cargar el GIF 😔", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ──────────────────────────────────────────────
    #  Comandos que requieren un usuario objetivo
    # ──────────────────────────────────────────────

    @commands.hybrid_command(name="hug", description="Abrasa a alguien")
    @app_commands.describe(target="Usuario al que quieres abrazar")
    async def hug(self, ctx: commands.Context, target: discord.Member):
        """Abrasa a otro usuario — &hug @usuario"""
        await self._send_action(ctx, "hug", "le dio un abrazo a", target=target, emoji="🤗")

    @commands.hybrid_command(name="kiss", description="Besa a alguien")
    @app_commands.describe(target="Usuario al que quieres besar")
    async def kiss(self, ctx: commands.Context, target: discord.Member):
        """Besa a otro usuario — &kiss @usuario"""
        await self._send_action(ctx, "kiss", "le dio un beso a", target=target, emoji="💋")

    @commands.hybrid_command(name="pat", description="Da una palmadita a alguien")
    @app_commands.describe(target="Usuario al que quieres darle una palmadita")
    async def pat(self, ctx: commands.Context, target: discord.Member):
        """Da una palmadita a otro usuario — &pat @usuario"""
        await self._send_action(ctx, "pat", "le dio una palmadita a", target=target, emoji="🤚")

    @commands.hybrid_command(name="slap", description="Abofetea a alguien")
    @app_commands.describe(target="Usuario al que quieres abofetear")
    async def slap(self, ctx: commands.Context, target: discord.Member):
        """Abofetea a otro usuario — &slap @usuario"""
        await self._send_action(ctx, "slap", "le dio una bofetada a", target=target, emoji="😲")

    @commands.hybrid_command(name="cuddle", description="Abrasa cariñosamente a alguien")
    @app_commands.describe(target="Usuario al que quieres abrazar cariñosamente")
    async def cuddle(self, ctx: commands.Context, target: discord.Member):
        """Abrasa cariñosamente a otro usuario — &cuddle @usuario"""
        await self._send_action(ctx, "cuddle", "le dio un abrazo cariñoso a", target=target, emoji="🥰")

    @commands.hybrid_command(name="poke", description="Molesta a alguien con un toque")
    @app_commands.describe(target="Usuario al que quieres molestar")
    async def poke(self, ctx: commands.Context, target: discord.Member):
        """Da un toque a otro usuario — &poke @usuario"""
        await self._send_action(ctx, "poke", "le dio un toque a", target=target, emoji="👉")

    @commands.hybrid_command(name="wave", description="Saluda a alguien")
    @app_commands.describe(target="Usuario al que quieres saludar")
    async def wave(self, ctx: commands.Context, target: discord.Member):
        """Saluda a otro usuario — &wave @usuario"""
        await self._send_action(ctx, "wave", "le saludó a", target=target, emoji="👋")

    # ──────────────────────────────────────────────
    #  Comandos AUTO-dirigidos (no requieren target)
    # ──────────────────────────────────────────────

    @commands.hybrid_command(name="dance", description="Ponte a bailar")
    async def dance(self, ctx: commands.Context):
        """Empieza a bailar — &dance"""
        await self._send_action(ctx, "dance", "se puso a bailar", emoji="🕺")

    @commands.hybrid_command(name="blush", description="Sonrojarse")
    async def blush(self, ctx: commands.Context):
        """Te sonrojas — &blush"""
        await self._send_action(ctx, "blush", "se sonrojó", emoji="😊")

    @commands.hybrid_command(name="smile", description="Sonríe")
    async def smile(self, ctx: commands.Context):
        """Sonríes — &smile"""
        await self._send_action(ctx, "smile", "sonrió", emoji="😄")


async def setup(bot):
    """Carga el cog Interaction en el bot"""
    if bot.get_cog("Interaction") is not None:
        return
    await bot.add_cog(Interaction(bot))

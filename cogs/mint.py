import discord
from discord.ext import commands
import os

class MintCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # GIFs mediante URL
        self.gifs_url = {
            "hazlotu": "https://cdn.discordapp.com/attachments/1249029432862310405/1488216155217854676/togif.gif",
            "venecos": "https://tenor.com/rRToQbUb6wk.gif",
            "feliz": "https://tenor.com/cOqRmS4Zjev.gif",
            "who": "https://tenor.com/q5XWIULZJnY.gif",
            "pendejo": "https://images-ext-1.discordapp.net/external/CGxMQ4A1x4YmcGMrksItfT4p1orZ3PxWGfllLmbCq7I/https/media.tenor.com/yFMN4ZGdv8AAAAPo/rigby-cat-rigby.mp4",
        }
        # GIFs como archivos locales
        self.gifs_file = {
            "proyectada": "gifs/proyectada.gif",
            "paja": "gifs/paja.gif",
            "afk": "gifs/afk.gif",
            "borren": "gifs/borren_el_server.mp4",
            "isthis": "gifs/is this.mp4",
        }

    @commands.hybrid_group(name="mint", invoke_without_command=True)
    async def mint(self, ctx):
        """Comandos de Mint: usa /mint hazlotu, /mint venecos, etc."""
        await ctx.send("❌ Debes especificar un subcomando. Usa `/mint hazlotu`, `/mint venecos`, etc.")

    @mint.command(name="hazlotu")
    async def mint_hazlotu(self, ctx):
        """Hazlo tú"""
        await ctx.send(self.gifs_url["hazlotu"])

    @mint.command(name="venecos")
    async def mint_venecos(self, ctx):
        """Pa' los venecos"""
        await ctx.send(self.gifs_url["venecos"])

    @mint.command(name="feliz")
    async def mint_feliz(self, ctx):
        """Cuando el mood está bien"""
        await ctx.send(self.gifs_url["feliz"])

    @mint.command(name="who")
    async def mint_who(self, ctx):
        """¿Quién?"""
        await ctx.send(self.gifs_url["who"])

    @mint.command(name="pendejo")
    async def mint_pendejo(self, ctx):
        """Rigby lo dice por ti"""
        await ctx.send(self.gifs_url["pendejo"])

    @mint.command(name="proyectada")
    async def mint_proyectada(self, ctx):
        """La proyectada de siempre"""
        ruta = self.gifs_file["proyectada"]
        if os.path.exists(ruta):
            await ctx.send(file=discord.File(ruta))
        else:
            await ctx.send(f"❌ No se encuentra el archivo `{ruta}`.")

    @mint.command(name="paja")
    async def mint_paja(self, ctx):
        """Sin comentarios"""
        ruta = self.gifs_file["paja"]
        if os.path.exists(ruta):
            await ctx.send(file=discord.File(ruta))
        else:
            await ctx.send(f"❌ No se encuentra el archivo `{ruta}`.")

    @mint.command(name="afk")
    async def mint_afk(self, ctx):
        """Me fui, chao"""
        ruta = self.gifs_file["afk"]
        if os.path.exists(ruta):
            await ctx.send(file=discord.File(ruta))
        else:
            await ctx.send(f"❌ No se encuentra el archivo `{ruta}`.")

    @mint.command(name="borren")
    async def mint_borren(self, ctx):
        """Nuclear option"""
        ruta = self.gifs_file["borren"]
        if os.path.exists(ruta):
            await ctx.send(file=discord.File(ruta))
        else:
            await ctx.send(f"❌ No se encuentra el archivo `{ruta}`.")

    @mint.command(name="isthis")
    async def mint_isthis(self, ctx):
        """¿Es esto...?"""
        ruta = self.gifs_file["isthis"]
        if os.path.exists(ruta):
            await ctx.send(file=discord.File(ruta))
        else:
            await ctx.send(f"❌ No se encuentra el archivo `{ruta}`.")

async def setup(bot):
    await bot.add_cog(MintCog(bot))
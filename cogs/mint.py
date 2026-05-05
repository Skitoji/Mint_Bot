import discord
from discord.ext import commands
import os

class MintCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # GIFs mediante URL (igual que en bot.py original)
        self.gifs_url = {
            "hazlo tu":  "https://cdn.discordapp.com/attachments/1249029432862310405/1488216155217854676/togif.gif",
            "venecos":   "https://tenor.com/rRToQbUb6wk.gif",
            "feliz":     "https://tenor.com/cOqRmS4Zjev.gif",
            "who":       "https://tenor.com/q5XWIULZJnY.gif",
            "pendejo":   "https://images-ext-1.discordapp.net/external/CGxMQ4A1x4YmcGMrksItfT4p1orZ3PxWGfllLmbCq7I/https/media.tenor.com/yFMN4ZGdv8AAAAPo/rigby-cat-rigby.mp4",
        }
        # GIFs como archivos locales (deben estar en la carpeta gifs/)
        self.gifs_file = {
            "proyectada":       "gifs/proyectada.gif",
            "paja":             "gifs/paja.gif",
            "afk":              "gifs/afk.gif",
            "borren el server": "gifs/borren_el_server.mp4",
            "is this":          "gifs/is this.mp4",
        }

    @commands.hybrid_group(name="mint", fallback="hazlo")
    async def mint(self, ctx, *, tema: str = "hazlo tu"):
        """Comandos temáticos de Mint (igual que el original)"""
        tema = tema.lower().strip()
        # Primero buscar en URLs
        if tema in self.gifs_url:
            await ctx.send(self.gifs_url[tema])
            return
        # Luego en archivos locales
        if tema in self.gifs_file:
            ruta = self.gifs_file[tema]
            if os.path.exists(ruta):
                await ctx.send(file=discord.File(ruta))
            else:
                await ctx.send(f"❌ No se encuentra el archivo `{ruta}`. Verifica la carpeta `gifs`.")
            return
        # Si no existe
        await ctx.send("❌ Tema no encontrado. Usa: `hazlo tu`, `venecos`, `feliz`, `who`, `pendejo`, `proyectada`, `paja`, `afk`, `borren el server`, `is this`")

    # Subcomandos individuales para autocompletado (igual que antes)
    @mint.command(name="hazlotu")
    async def mint_hazlotu(self, ctx):
        await self.mint(ctx, tema="hazlo tu")

    @mint.command(name="venecos")
    async def mint_venecos(self, ctx):
        await self.mint(ctx, tema="venecos")

    @mint.command(name="feliz")
    async def mint_feliz(self, ctx):
        await self.mint(ctx, tema="feliz")

    @mint.command(name="who")
    async def mint_who(self, ctx):
        await self.mint(ctx, tema="who")

    @mint.command(name="proyectada")
    async def mint_proyectada(self, ctx):
        await self.mint(ctx, tema="proyectada")

    @mint.command(name="pendejo")
    async def mint_pendejo(self, ctx):
        await self.mint(ctx, tema="pendejo")

    @mint.command(name="paja")
    async def mint_paja(self, ctx):
        await self.mint(ctx, tema="paja")

    @mint.command(name="afk")
    async def mint_afk(self, ctx):
        await self.mint(ctx, tema="afk")

    @mint.command(name="borren")
    async def mint_borren(self, ctx):
        await self.mint(ctx, tema="borren el server")

    @mint.command(name="isthis")
    async def mint_isthis(self, ctx):
        await self.mint(ctx, tema="is this")

async def setup(bot):
    await bot.add_cog(MintCog(bot))
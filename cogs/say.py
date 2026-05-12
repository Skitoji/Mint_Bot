import discord
from discord.ext import commands
from discord import app_commands
import re

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="say", description="Envía un mensaje o embed. &say texto o /say con opciones")
    @app_commands.describe(
        titulo="Título del embed (déjalo vacío para texto simple)",
        descripcion="Contenido principal o texto simple si es lo único que usas",
        canal="Canal donde enviar (opcional, por defecto este canal)",
        color="Color del embed (nombre en inglés)",
        imagen_url="URL de la imagen principal",
        miniatura_url="URL de la miniatura",
        footer_text="Texto en la parte inferior",
        campos="Campos extra: 'nombre|valor' separados por '||' (máx 5)",
        anonymous="True = no mostrar quién lo envió",
        mostrar_timestamp="True = agregar fecha/hora"
    )
    @app_commands.choices(color=[
        app_commands.Choice(name="🔴 Rojo", value="red"),
        app_commands.Choice(name="🟢 Verde", value="green"),
        app_commands.Choice(name="🔵 Azul", value="blue"),
        app_commands.Choice(name="🟡 Amarillo", value="yellow"),
        app_commands.Choice(name="🟣 Morado", value="purple"),
        app_commands.Choice(name="🟠 Naranja", value="orange"),
        app_commands.Choice(name="🌸 Rosa", value="pink"),
        app_commands.Choice(name="⚫ Negro", value="black"),
        app_commands.Choice(name="🌈 Personalizado", value="custom"),
    ])
    @commands.has_permissions(administrator=True)
    async def say(
        self,
        ctx,
        titulo: str = None,
        descripcion: str = None,
        canal: discord.TextChannel = None,
        color: app_commands.Choice[str] = None,
        imagen_url: str = None,
        miniatura_url: str = None,
        footer_text: str = None,
        campos: str = None,
        anonymous: bool = False,
        mostrar_timestamp: bool = False
    ):
        """&say texto — envía texto simple directo.
        &say título descripción — embed rápido.
        /say — interfaz completa con campos opcionales."""

        canal_destino = canal or ctx.channel
        es_slash = ctx.interaction is not None

        # 🟢 MODO TEXTO SIMPLE
        if descripcion is None and titulo is not None and not imagen_url and not miniatura_url and not campos and not footer_text and not color:
            await canal_destino.send(titulo)
            if es_slash:
                await ctx.send(f"✅ Mensaje enviado a {canal_destino.mention}", ephemeral=True)
            else:
                await ctx.send(f"✅ Mensaje enviado a {canal_destino.mention}")
            return

        # Si no hay título ni descripción, error
        if not titulo and not descripcion:
            if es_slash:
                await ctx.send("❌ Necesitas al menos título o descripción", ephemeral=True)
            else:
                await ctx.send("❌ Uso: `&say texto` o `&say título descripción`")
            return

        # 🟦 MODO EMBED
        color_embed = discord.Color.blue()
        if color:
            colores = {
                "red": discord.Color.red(),
                "green": discord.Color.green(),
                "blue": discord.Color.blue(),
                "yellow": discord.Color.yellow(),
                "purple": discord.Color.purple(),
                "orange": discord.Color.orange(),
                "pink": discord.Color.magenta(),
                "black": discord.Color.from_rgb(0, 0, 0),
                "custom": discord.Color.blue(),
            }
            color_embed = colores.get(color.value, discord.Color.blue())

        embed = discord.Embed(
            title=titulo or "",
            description=descripcion or "",
            color=color_embed
        )
        if mostrar_timestamp:
            embed.timestamp = ctx.message.created_at if ctx.message else discord.utils.utcnow()
        if imagen_url:
            embed.set_image(url=imagen_url)
        if miniatura_url:
            embed.set_thumbnail(url=miniatura_url)
        if footer_text:
            embed.set_footer(text=footer_text)
        elif not anonymous:
            embed.set_footer(text=f"Enviado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        if campos:
            partes = campos.split("||")
            if len(partes) > 5:
                msg = "❌ Máximo 5 campos permitidos."
                await (ctx.send(msg, ephemeral=True) if es_slash else ctx.send(msg))
                return
            for parte in partes:
                if "|" not in parte:
                    msg = f"❌ Formato inválido: `{parte}`. Usa 'nombre|valor'"
                    await (ctx.send(msg, ephemeral=True) if es_slash else ctx.send(msg))
                    return
                nombre, valor = parte.split("|", 1)
                embed.add_field(name=nombre.strip(), value=valor.strip(), inline=False)

        await canal_destino.send(embed=embed)
        msg = f"✅ Mensaje enviado a {canal_destino.mention}"
        await (ctx.send(msg, ephemeral=True) if es_slash else ctx.send(msg))


async def setup(bot):
    await bot.add_cog(Say(bot))

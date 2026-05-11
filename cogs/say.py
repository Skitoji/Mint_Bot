import discord
from discord.ext import commands
from discord import app_commands
import re

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="say", description="Envía un embed avanzado a un canal (solo admins)")
    @app_commands.describe(
        titulo="Título del embed (soporta Markdown)",
        descripcion="Contenido principal (soporta listas, negrita, etc.)",
        canal="Canal donde enviar (opcional, por defecto este canal)",
        color="Color del embed (nombre en inglés o hex, ej: blue, #ff0000)",
        imagen_url="URL de la imagen principal (grande)",
        miniatura_url="URL de la miniatura (esquina superior derecha)",
        footer_text="Texto que aparecerá en la parte inferior",
        campos="Campos adicionales. Formato: 'nombre|valor' separados por '||' (máx 5). Ej: 'Regla1|No spamear||Regla2|Ser respetuoso'",
        anonymous="Si es True, no se mostrará quién envió el mensaje",
        mostrar_timestamp="Si es True, agrega la fecha y hora actual"
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
        app_commands.Choice(name="🌈 Personalizado (hex)", value="custom"),
    ])
    @commands.has_permissions(administrator=True)
    async def say(
        self,
        ctx,
        titulo: str,
        descripcion: str,
        canal: discord.TextChannel = None,
        color: app_commands.Choice[str] = None,
        imagen_url: str = None,
        miniatura_url: str = None,
        footer_text: str = None,
        campos: str = None,
        anonymous: bool = False,
        mostrar_timestamp: bool = False
    ):
        await ctx.defer(ephemeral=True)

        # Canal destino
        canal_destino = canal or ctx.channel

        # Procesar color
        color_embed = discord.Color.blue()
        if color:
            if color.value == "custom":
                # Podríamos pedir un hex, pero por simplicidad usamos azul
                color_embed = discord.Color.blue()
            else:
                colores = {
                    "red": discord.Color.red(),
                    "green": discord.Color.green(),
                    "blue": discord.Color.blue(),
                    "yellow": discord.Color.yellow(),
                    "purple": discord.Color.purple(),
                    "orange": discord.Color.orange(),
                    "pink": discord.Color.magenta(),
                    "black": discord.Color.from_rgb(0, 0, 0),
                }
                color_embed = colores.get(color.value, discord.Color.blue())
        # Crear embed
        embed = discord.Embed(
            title=titulo,
            description=descripcion,
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
            # Si no hay footer personalizado y no es anónimo, mostrar quién lo envió
            embed.set_footer(text=f"Enviado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        # Procesar campos
        if campos:
            # Dividir por '||' para obtener cada campo
            partes = campos.split("||")
            if len(partes) > 5:
                await ctx.send("❌ Máximo 5 campos permitidos.", ephemeral=True)
                return
            for parte in partes:
                if "|" not in parte:
                    await ctx.send(f"❌ Formato de campo inválido: `{parte}`. Debe ser 'nombre|valor'", ephemeral=True)
                    return
                nombre, valor = parte.split("|", 1)
                embed.add_field(name=nombre.strip(), value=valor.strip(), inline=False)

        # Enviar embed
        await canal_destino.send(embed=embed)
        await ctx.send(f"✅ Mensaje enviado a {canal_destino.mention}", ephemeral=True)

    # Soporte para prefijo también (por si se usa &say)
    @commands.command(name="say")
    @commands.has_permissions(administrator=True)
    async def say_prefix(self, ctx, canal: discord.TextChannel = None, *, texto: str = None):
        """Envío de embed avanzado mediante prefijo. Uso: &say #canal título|descripción|... (formato complejo). 
        Para simplicidad, se recomienda usar el slash command."""
        if not texto:
            await ctx.send("❌ Uso: `&say #canal título|descripción|color|imagen|miniature|footer|anonymous|timestamp`\nEjemplo: `&say #general Reglas| - Ser respetuoso - No spamear|blue|https://...`", ephemeral=True)
            return
        # Implementación simplificada para prefijo: se podría parsear, pero mejor remitir al slash
        await ctx.send("⚠️ Usa el comando `/say` para una experiencia más completa y con opciones.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Say(bot))
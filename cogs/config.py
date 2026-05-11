import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
import json
import os
from typing import Optional, Literal

# ──────────────────────────────────────────────
# ARCHIVOS DE CONFIGURACIÓN
# ──────────────────────────────────────────────
WELCOME_CONFIG_FILE = "data/welcome_config.json"
GUILD_CONFIG_FILE = "data/guild_config.json"

# ─── Welcome Config (legacy) ──────────────────
def load_welcome_config():
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(WELCOME_CONFIG_FILE):
        with open(WELCOME_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_welcome_config(data):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(WELCOME_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── Guild Config (nuevo) ─────────────────────
def load_all_guild_configs():
    """Carga todo el archivo guild_config.json"""
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(GUILD_CONFIG_FILE):
        with open(GUILD_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_all_guild_configs(data):
    """Guarda todo el archivo guild_config.json"""
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(GUILD_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_guild_config(guild_id: int) -> dict:
    """Obtiene la configuración de un servidor específico."""
    all_configs = load_all_guild_configs()
    guild_key = str(guild_id)
    if guild_key not in all_configs:
        all_configs[guild_key] = {
            "prefix": "&",
            "antilinks": False,
            "blacklist": [],
            "autorole": None,
            "log_channel": None,
            "suggestions_channel": None,
            "polls_enabled": False
        }
        save_all_guild_configs(all_configs)
    return all_configs[guild_key]

def set_guild_config(guild_id: int, key: str, value):
    """Establece un valor en la configuración de un servidor."""
    all_configs = load_all_guild_configs()
    guild_key = str(guild_id)
    if guild_key not in all_configs:
        all_configs[guild_key] = {
            "prefix": "&",
            "antilinks": False,
            "blacklist": [],
            "autorole": None,
            "log_channel": None,
            "suggestions_channel": None,
            "polls_enabled": False
        }
    all_configs[guild_key][key] = value
    save_all_guild_configs(all_configs)

def get_gif_list():
    gifs_folder = "gifs"
    if not os.path.exists(gifs_folder):
        return []
    return [f for f in os.listdir(gifs_folder) if f.lower().endswith(('.gif', '.mp4'))]

# ── MODALES (Welcome Config) ──────────────────
class TitleModal(ui.Modal, title="Editar Título"):
    def __init__(self, current_value, original_message):
        super().__init__()
        self.original_message = original_message
        self.title_input = ui.TextInput(label="Nuevo título", default=current_value, max_length=256)
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_welcome_config()
        config['welcome_title'] = self.title_input.value
        save_welcome_config(config)
        await interaction.response.send_message("✅ Título actualizado", ephemeral=True)
        embed = create_dashboard_embed()
        await self.original_message.edit(embed=embed, view=DashboardView(self.original_message))

class DescModal(ui.Modal, title="Editar Descripción"):
    def __init__(self, current_value, original_message):
        super().__init__()
        self.original_message = original_message
        self.desc_input = ui.TextInput(label="Nueva descripción", style=discord.TextStyle.paragraph, default=current_value, max_length=1000)
        self.add_item(self.desc_input)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_welcome_config()
        config['welcome_description'] = self.desc_input.value
        save_welcome_config(config)
        await interaction.response.send_message("✅ Descripción actualizada", ephemeral=True)
        embed = create_dashboard_embed()
        await self.original_message.edit(embed=embed, view=DashboardView(self.original_message))

class FooterModal(ui.Modal, title="Editar Footer"):
    def __init__(self, current_value, original_message):
        super().__init__()
        self.original_message = original_message
        self.footer_input = ui.TextInput(label="Nuevo footer", default=current_value, max_length=256)
        self.add_item(self.footer_input)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_welcome_config()
        config['footer_text'] = self.footer_input.value
        save_welcome_config(config)
        await interaction.response.send_message("✅ Footer actualizado", ephemeral=True)
        embed = create_dashboard_embed()
        await self.original_message.edit(embed=embed, view=DashboardView(self.original_message))

# ── SELECTORES (Welcome Config) ───────────────
class GifSelect(ui.Select):
    def __init__(self, original_message):
        options = [discord.SelectOption(label=gif) for gif in get_gif_list()[:25]]
        super().__init__(placeholder="Selecciona un GIF", options=options)
        self.original_message = original_message

    async def callback(self, interaction: discord.Interaction):
        config = load_welcome_config()
        config['welcome_image'] = self.values[0]
        save_welcome_config(config)
        await interaction.response.send_message(f"✅ GIF seleccionado: {self.values[0]}", ephemeral=True)
        embed = create_dashboard_embed()
        await self.original_message.edit(embed=embed, view=DashboardView(self.original_message))

class ChannelSelect(ui.ChannelSelect):
    def __init__(self, original_message):
        super().__init__(placeholder="Selecciona un canal", channel_types=[discord.ChannelType.text])
        self.original_message = original_message

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        config = load_welcome_config()
        config['channel_id'] = channel.id
        save_welcome_config(config)
        await interaction.response.send_message(f"✅ Canal establecido: {channel.mention}", ephemeral=True)
        embed = create_dashboard_embed()
        await self.original_message.edit(embed=embed, view=DashboardView(self.original_message))

# ── VISTA PRINCIPAL (Dashboard Welcome) ───────
class DashboardView(ui.View):
    def __init__(self, original_message):
        super().__init__(timeout=None)
        self.original_message = original_message

    @ui.button(label="📢 Seleccionar canal", style=discord.ButtonStyle.primary)
    async def select_channel(self, interaction: discord.Interaction, button: ui.Button):
        view = ui.View(timeout=60)
        view.add_item(ChannelSelect(self.original_message))
        await interaction.response.send_message("Selecciona el canal de bienvenida:", view=view, ephemeral=True)

    @ui.button(label="🖼️ Seleccionar GIF", style=discord.ButtonStyle.success)
    async def select_gif(self, interaction: discord.Interaction, button: ui.Button):
        if not get_gif_list():
            await interaction.response.send_message("❌ No hay GIFs en la carpeta `gifs/`.", ephemeral=True)
            return
        view = ui.View(timeout=60)
        view.add_item(GifSelect(self.original_message))
        await interaction.response.send_message("Selecciona un GIF:", view=view, ephemeral=True)

    @ui.button(label="✏️ Editar Título", style=discord.ButtonStyle.secondary)
    async def edit_title(self, interaction: discord.Interaction, button: ui.Button):
        config = load_welcome_config()
        current = config.get("welcome_title", "")
        modal = TitleModal(current, self.original_message)
        await interaction.response.send_modal(modal)

    @ui.button(label="📝 Editar Descripción", style=discord.ButtonStyle.secondary)
    async def edit_desc(self, interaction: discord.Interaction, button: ui.Button):
        config = load_welcome_config()
        current = config.get("welcome_description", "")
        modal = DescModal(current, self.original_message)
        await interaction.response.send_modal(modal)

    @ui.button(label="🔽 Editar Footer", style=discord.ButtonStyle.secondary)
    async def edit_footer(self, interaction: discord.Interaction, button: ui.Button):
        config = load_welcome_config()
        current = config.get("footer_text", "Mint")
        modal = FooterModal(current, self.original_message)
        await interaction.response.send_modal(modal)

    @ui.button(label="🧪 Probar Bienvenida", style=discord.ButtonStyle.danger)
    async def test_welcome(self, interaction: discord.Interaction, button: ui.Button):
        welcome_cog = interaction.client.get_cog("Welcome")
        if welcome_cog:
            await interaction.response.send_message("🔄 Enviando mensaje de prueba...", ephemeral=True)
            await welcome_cog.emit_test_welcome(interaction.user)
        else:
            await interaction.response.send_message("❌ Cog 'Welcome' no cargado.", ephemeral=True)

    @ui.button(label="🔄 Actualizar Dashboard", style=discord.ButtonStyle.grey)
    async def refresh(self, interaction: discord.Interaction, button: ui.Button):
        embed = create_dashboard_embed()
        await interaction.response.edit_message(embed=embed, view=self)

# ── EMBED DEL DASHBOARD (Welcome) ─────────────
def create_dashboard_embed():
    config = load_welcome_config()
    embed = discord.Embed(
        title="🛠️ Dashboard de Configuración",
        description="Configura las bienvenidas. Usa los botones.\n\n*Emojis personalizados: `<:nombre:id>`*",
        color=discord.Color.dark_grey()
    )
    channel = config.get('channel_id')
    channel_mention = f"<#{channel}>" if channel else "❌ No configurado"
    preview = (
        f"**Canal:** {channel_mention}\n"
        f"**Título:** {config.get('welcome_title', 'No configurado')}\n"
        f"**Descripción:** {config.get('welcome_description', '{mention}')}\n"
        f"**Footer:** {config.get('footer_text', 'Mint')}\n"
        f"**GIF:** {config.get('welcome_image', 'Ninguno')}"
    )
    embed.add_field(name="📋 Configuración actual", value=preview, inline=False)
    return embed

# ── AUTOCOMPLETADO PARA CATEGORÍAS ────────────
TRIVIA_CATEGORIES = {
    "General": 9,
    "Libros": 10,
    "Cine": 11,
    "Música": 12,
    "Videojuegos": 15,
    "Ciencia": 17,
    "Historia": 23,
    "Geografía": 22,
    "Deportes": 21,
    "Arte": 25,
    "Celebridades": 26,
    "Animales": 27,
}

# ══════════════════════════════════════════════
#  COG PRINCIPAL
# ══════════════════════════════════════════════
class Config(commands.Cog):
    """Configuración del servidor — Bienvenidas y ajustes generales"""

    def __init__(self, bot):
        self.bot = bot

    # ── Comando hibrido existente ──────────────
    @commands.hybrid_command(name="dashboard", description="Abre el panel de configuración de bienvenidas")
    @commands.has_permissions(administrator=True)
    async def dashboard(self, ctx):
        await ctx.defer()
        embed = create_dashboard_embed()
        msg = await ctx.send(embed=embed, view=None)
        view = DashboardView(msg)
        await msg.edit(embed=embed, view=view)

    # ==========================================
    #  NUEVOS SLASH COMMANDS - CONFIG DEL SERVIDOR
    # ==========================================

    # ── /config-prefix ─────────────────────────
    @app_commands.command(name="config-prefix", description="Establece el prefijo personalizado del servidor (máx. 3 caracteres)")
    @app_commands.default_permissions(administrator=True)
    async def config_prefix(self, interaction: discord.Interaction, prefix: str):
        """Cambia el prefijo del servidor."""
        if len(prefix) > 3:
            embed = discord.Embed(
                title="❌ Prefijo demasiado largo",
                description="El prefijo no puede tener más de **3 caracteres**.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        set_guild_config(interaction.guild_id, "prefix", prefix)
        embed = discord.Embed(
            title="🔧 Prefijo Actualizado",
            description=f"El nuevo prefijo del servidor es **`{prefix}`**",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Configurado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /config-antilinks ──────────────────────
    @app_commands.command(name="config-antilinks", description="Activa o desactiva la protección anti-enlaces de invitación")
    @app_commands.default_permissions(administrator=True)
    async def config_antilinks(self, interaction: discord.Interaction, estado: Literal["on", "off"]):
        """Activa/desactiva la protección anti-invites."""
        valor = estado == "on"
        set_guild_config(interaction.guild_id, "antilinks", valor)

        if valor:
            embed = discord.Embed(
                title="🔒 Anti-Links Activado",
                description="Los mensajes que contengan enlaces de invitación a otros servidores serán eliminados automáticamente.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="🔓 Anti-Links Desactivado",
                description="La protección anti-invitaciones ha sido desactivada.",
                color=discord.Color.red()
            )
        embed.set_footer(text=f"Configurado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /config-filter ─────────────────────────
    @app_commands.command(name="config-filter", description="Gestiona las palabras bloqueadas en el servidor")
    @app_commands.default_permissions(administrator=True)
    async def config_filter(self, interaction: discord.Interaction, accion: Literal["add", "remove", "list"], palabra: Optional[str] = None):
        """Añade, elimina o lista palabras de la lista negra."""
        config = get_guild_config(interaction.guild_id)

        if accion == "add":
            if not palabra:
                await interaction.response.send_message("❌ Debes especificar una palabra para añadir.", ephemeral=True)
                return
            palabra_lower = palabra.lower()
            if palabra_lower in config["blacklist"]:
                embed = discord.Embed(
                    title="⚠️ Ya existe",
                    description=f"La palabra **`{palabra_lower}`** ya está en la lista negra.",
                    color=discord.Color.orange()
                )
            else:
                config["blacklist"].append(palabra_lower)
                set_guild_config(interaction.guild_id, "blacklist", config["blacklist"])
                embed = discord.Embed(
                    title="✅ Palabra Bloqueada",
                    description=f"**`{palabra_lower}`** ha sido añadida a la lista negra.",
                    color=discord.Color.green()
                )

        elif accion == "remove":
            if not palabra:
                await interaction.response.send_message("❌ Debes especificar una palabra para eliminar.", ephemeral=True)
                return
            palabra_lower = palabra.lower()
            if palabra_lower in config["blacklist"]:
                config["blacklist"].remove(palabra_lower)
                set_guild_config(interaction.guild_id, "blacklist", config["blacklist"])
                embed = discord.Embed(
                    title="✅ Palabra Eliminada",
                    description=f"**`{palabra_lower}`** ha sido eliminada de la lista negra.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ No encontrada",
                    description=f"**`{palabra_lower}`** no está en la lista negra.",
                    color=discord.Color.red()
                )

        else:  # list
            blacklist = config.get("blacklist", [])
            if not blacklist:
                embed = discord.Embed(
                    title="📋 Lista Negra",
                    description="No hay palabras bloqueadas en este servidor.",
                    color=discord.Color.blue()
                )
            else:
                palabras_formateadas = "\n".join([f"• `{p}`" for p in blacklist])
                embed = discord.Embed(
                    title="📋 Lista Negra de Palabras",
                    description=palabras_formateadas,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Total: {len(blacklist)} palabra(s)")

        embed.set_footer(text=f"Configurado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /config-autorole ───────────────────────
    @app_commands.command(name="config-autorole", description="Establece el rol automático para nuevos miembros")
    @app_commands.default_permissions(administrator=True)
    async def config_autorole(self, interaction: discord.Interaction, rol: discord.Role):
        """Asigna un rol automático a los nuevos miembros."""
        if rol >= interaction.user.top_role and interaction.guild.owner_id != interaction.user.id:
            embed = discord.Embed(
                title="❌ Rol inválido",
                description="No puedes asignar un rol superior o igual a tu propio rol más alto.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if rol.is_default():
            embed = discord.Embed(
                title="❌ Rol inválido",
                description="No puedes usar el rol `@everyone` como auto-rol.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        set_guild_config(interaction.guild_id, "autorole", rol.id)
        embed = discord.Embed(
            title="🎖️ Auto-Rol Configurado",
            description=f"Los nuevos miembros recibirán automáticamente el rol {rol.mention}.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Configurado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /config-logs ───────────────────────────
    @app_commands.command(name="config-logs", description="Establece el canal de registros de moderación")
    @app_commands.default_permissions(administrator=True)
    async def config_logs(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Define el canal donde se enviarán los logs de moderación."""
        set_guild_config(interaction.guild_id, "log_channel", canal.id)
        embed = discord.Embed(
            title="📜 Canal de Logs Configurado",
            description=f"Los registros de moderación se enviarán a {canal.mention}.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Configurado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /config-suggestions ────────────────────
    @app_commands.command(name="config-suggestions", description="Activa/desactiva el sistema de sugerencias con un canal")
    @app_commands.default_permissions(administrator=True)
    async def config_suggestions(self, interaction: discord.Interaction, estado: Literal["on", "off"], canal: Optional[discord.TextChannel] = None):
        """Habilita o deshabilita el sistema de sugerencias."""
        if estado == "on" and not canal:
            await interaction.response.send_message(
                "❌ Debes especificar un canal cuando activas las sugerencias.", ephemeral=True
            )
            return

        if estado == "on":
            set_guild_config(interaction.guild_id, "suggestions_channel", canal.id)
            embed = discord.Embed(
                title="💡 Sugerencias Activadas",
                description=f"El sistema de sugerencias ha sido activado. Los usuarios podrán enviar sus sugerencias en {canal.mention}.",
                color=discord.Color.green()
            )
        else:
            set_guild_config(interaction.guild_id, "suggestions_channel", None)
            embed = discord.Embed(
                title="💡 Sugerencias Desactivadas",
                description="El sistema de sugerencias ha sido desactivado.",
                color=discord.Color.red()
            )
        embed.set_footer(text=f"Configurado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /config-polls ──────────────────────────
    @app_commands.command(name="config-polls", description="Activa o desactiva el sistema de encuestas")
    @app_commands.default_permissions(administrator=True)
    async def config_polls(self, interaction: discord.Interaction, estado: Literal["on", "off"]):
        """Habilita o deshabilita la creación de encuestas."""
        valor = estado == "on"
        set_guild_config(interaction.guild_id, "polls_enabled", valor)

        if valor:
            embed = discord.Embed(
                title="📊 Encuestas Activadas",
                description="Los usuarios podrán crear y participar en encuestas.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="📊 Encuestas Desactivadas",
                description="La creación de encuestas ha sido desactivada.",
                color=discord.Color.red()
            )
        embed.set_footer(text=f"Configurado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── Comando para ver configuración actual ──
    @app_commands.command(name="config-show", description="Muestra la configuración actual del servidor")
    @app_commands.default_permissions(administrator=True)
    async def config_show(self, interaction: discord.Interaction):
        """Muestra toda la configuración del servidor en un embed."""
        config = get_guild_config(interaction.guild_id)

        embed = discord.Embed(
            title="⚙️ Configuración del Servidor",
            description=f"Configuración actual de **{interaction.guild.name}**",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

        # Prefijo
        embed.add_field(name="🔤 Prefijo", value=f"`{config.get('prefix', '&')}`", inline=True)

        # Anti-links
        antilinks = config.get("antilinks", False)
        embed.add_field(name="🔗 Anti-Links", value="✅ Activado" if antilinks else "❌ Desactivado", inline=True)

        # Auto-rol
        autorole_id = config.get("autorole")
        if autorole_id:
            role = interaction.guild.get_role(autorole_id)
            autorole_text = role.mention if role else f"`ID: {autorole_id}`"
        else:
            autorole_text = "❌ No configurado"
        embed.add_field(name="🎖️ Auto-Rol", value=autorole_text, inline=True)

        # Canal de logs
        log_id = config.get("log_channel")
        log_text = f"<#{log_id}>" if log_id else "❌ No configurado"
        embed.add_field(name="📜 Canal de Logs", value=log_text, inline=True)

        # Sugerencias
        sugg_id = config.get("suggestions_channel")
        sugg_text = f"<#{sugg_id}>" if sugg_id else "❌ Desactivado"
        embed.add_field(name="💡 Sugerencias", value=sugg_text, inline=True)

        # Encuestas
        polls = config.get("polls_enabled", False)
        embed.add_field(name="📊 Encuestas", value="✅ Activadas" if polls else "❌ Desactivadas", inline=True)

        # Palabras bloqueadas
        blacklist = config.get("blacklist", [])
        if blacklist:
            palabras = ", ".join([f"`{p}`" for p in blacklist[:10]])
            if len(blacklist) > 10:
                palabras += f" y {len(blacklist) - 10} más..."
            embed.add_field(name="🚫 Palabras Bloqueadas", value=palabras, inline=False)
        else:
            embed.add_field(name="🚫 Palabras Bloqueadas", value="Ninguna", inline=True)

        await interaction.response.send_message(embed=embed)

# ── SETUP ─────────────────────────────────────
async def setup(bot):
    if bot.get_cog("Config") is not None:
        print("⚠️ Cog 'Config' ya cargado - omitiendo carga duplicada")
        return
    await bot.add_cog(Config(bot))

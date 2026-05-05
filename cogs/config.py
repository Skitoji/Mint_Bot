import discord
from discord.ext import commands
from discord import ui
import json
import os

WELCOME_CONFIG_FILE = "data/welcome_config.json"

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

def get_gif_list():
    gifs_folder = "gifs"
    if not os.path.exists(gifs_folder):
        return []
    return [f for f in os.listdir(gifs_folder) if f.lower().endswith(('.gif', '.mp4'))]

# ---------- MODALES ----------
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
        # Refrescar el dashboard
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

# ---------- SELECTORES ----------
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

# ---------- VISTA PRINCIPAL ----------
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

# ---------- EMBED DEL DASHBOARD ----------
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

# ---------- COG ----------
class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="dashboard", description="Abre el panel de configuración")
    @commands.has_permissions(administrator=True)
    async def dashboard(self, ctx):
        await ctx.defer()
        embed = create_dashboard_embed()
        msg = await ctx.send(embed=embed, view=None)
        view = DashboardView(msg)
        await msg.edit(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Config(bot))
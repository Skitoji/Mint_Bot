import discord
from discord.ext import commands
import json
import os

def cargar_contador():
    if not os.path.exists("data"):
        os.makedirs("data")
    archivo = "data/contador.txt"
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                content = f.read().strip()
                return int(content) if content else 0
        except:
            return 0
    return 0

def guardar_contador(num):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open("data/contador.txt", "w") as f:
        f.write(str(num))

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.contador = cargar_contador()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"🔔 Miembro unido: {member}")

        config_file = "data/welcome_config.json"
        if not os.path.exists(config_file):
            print("❌ No existe welcome_config.json")
            return

        with open(config_file, "r") as f:
            config = json.load(f)

        channel_id = config.get("channel_id")
        if not channel_id:
            print("❌ No hay channel_id")
            return

        self.contador += 1
        guardar_contador(self.contador)

        title = config.get("welcome_title", "Bienvenid@!")
        desc_template = config.get("welcome_description", "Bienvenid@ {mention}")
        desc = desc_template.replace("{mention}", member.mention).replace("{count}", str(self.contador)).replace("{server}", member.guild.name)
        footer = config.get("footer_text", "Mint").replace("{count}", str(self.contador))
        gif_filename = config.get("welcome_image")

        # DM
        dm_text = f"{desc}\n\nEres el usuario n° **{self.contador}**"
        dm_file = None
        if gif_filename:
            gif_path = os.path.join("gifs", gif_filename)
            if os.path.exists(gif_path):
                dm_file = discord.File(gif_path, filename=gif_filename)
        try:
            if dm_file:
                await member.send(content=dm_text, file=dm_file)
            else:
                await member.send(dm_text)
        except Exception as e:
            print(f"DM fallido: {e}")

        # Embed en canal
        canal = member.guild.get_channel(int(channel_id))
        if canal:
            embed = discord.Embed(title=title, description=desc, color=discord.Color.from_rgb(255, 20, 90))
            embed.set_thumbnail(url=member.display_avatar.url)
            if footer:
                embed.set_footer(text=footer)
            if gif_filename:
                gif_path = os.path.join("gifs", gif_filename)
                if os.path.exists(gif_path):
                    file = discord.File(gif_path, filename=gif_filename)
                    embed.set_image(url=f"attachment://{gif_filename}")
                    await canal.send(embed=embed, file=file)
                else:
                    await canal.send(embed=embed)
            else:
                await canal.send(embed=embed)
            print(f"✅ Bienvenida enviada a {canal.name}")
        else:
            print(f"❌ Canal no encontrado: {channel_id}")

    async def emit_test_welcome(self, member):
        await self.on_member_join(member)

    @commands.hybrid_command(description="Prueba el mensaje de bienvenida")
    @commands.has_permissions(administrator=True)
    async def testwelcome(self, ctx):
        await ctx.defer(ephemeral=True)
        await self.emit_test_welcome(ctx.author)
        await ctx.send("✅ Mensaje de prueba enviado (si estaba configurado)", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
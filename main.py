import discord
from discord.ext import commands
import os
import json
import subprocess
import asyncio

# ==========================================
# VERIFICAR FFMPEG (para música)
# ==========================================
def check_ffmpeg():
    """Verificar si FFmpeg está instalado en el sistema"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg encontrado")
            return True
    except:
        pass
    print("⚠️ FFmpeg no encontrado. El bot funcionará, pero la música no estará disponible.")
    print("   Para instalarlo en Windows: descarga de https://ffmpeg.org/download.html y agrégalo al PATH.")
    print("   En Linux: sudo apt install ffmpeg")
    return False

# ==========================================
# CARGAR CONFIGURACIÓN
# ==========================================
CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print(f"❌ No se encuentra {CONFIG_FILE}. Crea uno con:")
    print('{"TOKEN": "TU_TOKEN", "PREFIX": "&"}')
    exit(1)

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

TOKEN = config.get("TOKEN")
PREFIX = config.get("PREFIX", "&")

if not TOKEN:
    print("❌ No se encontró TOKEN en config.json")
    exit(1)

# ==========================================
# INTENTS (necesitas activarlos en Discord Dev Portal)
# ==========================================
intents = discord.Intents.default()
intents.members = True          # Necesario para niveles y perfiles
intents.message_content = True  # Necesario para comandos con prefijo (&)

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.config = config

# ==========================================
# CARGA AUTOMÁTICA DE COGS
# ==========================================
async def load_cogs():
    cogs_dir = "./cogs"
    if not os.path.isdir(cogs_dir):
        print(f"❌ No existe la carpeta {cogs_dir}")
        return

    loaded = 0
    for file in os.listdir(cogs_dir):
        if file.endswith(".py") and not file.startswith("__"):
            try:
                cog_name = file[:-3]
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"⚙ Cog cargado → {file}")
                loaded += 1
            except Exception as e:
                print(f"❌ Error cargando {file}: {e}")
    print(f"✅ Total cogs cargados: {loaded}")

# ==========================================
# EVENTO ON_READY
# ==========================================
@bot.event
async def on_ready():
    print(f"\n🚀 Bot iniciado correctamente como {bot.user} (ID: {bot.user.id})")
    print(f"🔧 Prefix: {PREFIX}")
    check_ffmpeg()
    print("-" * 40)

    # Sincronizar comandos slash (puede tardar hasta 1 hora en propagarse)
    try:
        synced = await bot.tree.sync()
        print(f"✅ Comandos slash sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error sincronizando comandos slash: {e}")

# ==========================================
# MAIN
# ==========================================
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
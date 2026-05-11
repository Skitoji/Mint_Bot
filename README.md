# 🌿 Mint Bot

> *Inspirado en **Mint**, la enigmática y poderosa personaje de *Neverness to Everness (NTE)*.*

Mint Bot es un bot de Discord moderno, escrito en Python con `discord.py`. Está diseñado para gestionar y entretener tu servidor con estilo: GIFs, moderación, música, economía, casino, trading, niveles, juegos y mucho más.

---

## ✨ Características principales

| Módulo | Funcionalidades |
|--------|----------------|
| 🌿 **Mint** | GIFs temáticos y respuestas con actitud |
| 🛡️ **Moderación** | Warn, mute, kick, ban, timeout, snipe, slowmode, lock, voz y más |
| 🎵 **Música** | Reproducción desde YouTube/Spotify (FFmpeg) |
| 💰 **Economía** | Monedas, trabajos, banco, apuestas, transferencias |
| 🎰 **Casino** | Slots, Crash, Mines, Plinko, Dice |
| 📊 **Trading** | Mercado de acciones y cryptos (compra/venta/portfolio) |
| 📈 **Niveles (XP)** | Sistema de experiencia por mensajes + leaderboards |
| 💍 **Perfiles** | Perfil personalizable, biografía, matrimonio |
| 🎮 **Diversión** | 8ball, trivia, memes, juegos multijugador, texto loco |
| 🤗 **Interacción** | Hug, kiss, pat, slap, cuddle y más con GIFs anime |
| ℹ️ **Información** | Avatar, serverinfo, userinfo, ping, etc. |
| ⚙️ **Configuración** | Bienvenidas, antilinks, blacklist, autoroles, prefix |

---

## 🎮 Lista completa de comandos

Todos los comandos están disponibles como **slash commands** (`/`) y también con prefijo (`&`).

### 🌿 Mint (GIFs)
`/mint hazlotu` · `/mint venecos` · `/mint feliz` · `/mint who` · `/mint proyectada` · `/mint pendejo` · `/mint paja` · `/mint afk` · `/mint borren` · `/mint isthis`

### 🛡️ Moderación
`/warn` · `/warns` · `/clearwarns` · `/kick` · `/ban` · `/unban` · `/tempban` · `/mute` · `/unmute` · `/timeout` · `/untimeout` · `/slowmode` · `/lock` · `/unlock` · `/clear` · `/snipe` · `/esnipe` · `/voicekick` · `/voicemove` · `/vcmute` · `/vcunmute`

### 🎵 Música
`/play` · `/pause` · `/resume` · `/skip` · `/stop` · `/queue` · `/nowplaying` · `/loop` · `/shuffle` · `/volume` · `/disconnect`

### 💰 Economía
`/balance` · `/daily` · `/weekly` · `/work` · `/deposit` · `/withdraw` · `/bank` · `/gamble` · `/pagar` · `/leaderboard coins`

### 🎰 Casino
`/slots` · `/crash` · `/mines` · `/plinko` · `/dice` · `/casino-stats`

### 📊 Trading
`/stocks` · `/buy` · `/sell` · `/portfolio` · `/stonks` · `/price`

### 🎮 Diversión
`/8ball` · `/coinflip` · `/dice` · `/choose` · `/howgay` · `/lovecalc` · `/ascii` · `/reverse` · `/bigtext` · `/owoify` · `/meme` · `/waifu` · `/nekogirl` · `/trivia` · `/randomnumber`

### 🤗 Interacción
`/hug` · `/kiss` · `/pat` · `/slap` · `/cuddle` · `/bonk` · `/bite` · `/punch` · `/dance` · `/blurp`

### 🎲 Juegos multijugador
`/snake` · `/connect4` · `/tictactoe` · `/rps`

### 👤 Perfil & Niveles
`/perfil` · `/bio` · `/level` · `/marry` · `/divorce` · `/leaderboard xp` · `/leaderboard marriage`

### ℹ️ Información
`/ping` · `/avatar` · `/banner` · `/serverinfo` · `/userinfo` · `/roleinfo` · `/channelinfo` · `/servericon` · `/botinfo` · `/invite` · `/comandos`

### ⚙️ Configuración
`/dashboard` · `/testwelcome` · `/antilinks` · `/blacklist` · `/autorole` · `/prefix` · `/creacolores` · `/autorroles`

### 🔧 Admin (owner)
`/reload` · `/load` · `/unload` · `/sync` · `/addcoins` · `/removecoins` · `/setlevel` · `/serverlist` · `/botstatus`

---

## 🚀 Instalación

### Requisitos
- Python 3.11+
- FFmpeg (para música)
- Token de bot de Discord

### Pasos
```bash
# Clonar el repositorio
git clone https://github.com/Skitoji/Mint_Bot.git
cd Mint_Bot

# Instalar dependencias
pip install -r requirements.txt

# Configurar token
echo "DISCORD_TOKEN=tu_token_aqui" > .env

# Ejecutar
python main.py
```

### FFmpeg
```bash
# Linux
sudo apt install ffmpeg

# Windows
# Descargar de https://ffmpeg.org/download.html y agregar al PATH
```

---

## 📁 Estructura del proyecto

```
Mint_Bot/
├── main.py              # Entry point del bot
├── requirements.txt     # Dependencias
├── install_ffmpeg.py    # Helper para instalar FFmpeg
├── cogs/
│   ├── admin.py         # Comandos de administración
│   ├── autoroles.py     # Sistema de roles de colores
│   ├── casino.py        # 🎰 Slots, Crash, Mines, Plinko, Dice
│   ├── config.py        # Dashboard de bienvenidas
│   ├── economy.py       # 💰 Economía y banco
│   ├── fun.py           # 🎮 Diversión, juegos, memes
│   ├── games.py         # 🎲 Juegos multijugador
│   ├── giveaways.py     # Sistema de sorteos
│   ├── help.py          # 📖 Comando /comandos
│   ├── info.py          # ℹ️ Información del servidor/usuarios
│   ├── interaction.py   # 🤗 Interacción social con GIFs
│   ├── leaderboards.py  # 🏆 Rankings
│   ├── mint.py          # 🌿 Comandos Mint (GIFs)
│   ├── moderation.py    # 🛡️ Moderación completa
│   ├── music.py         # 🎵 Música
│   ├── profile.py       # 👤 Perfiles y matrimonio
│   ├── say.py           # Anuncios embed
│   ├── trading.py       # 📊 Trading de acciones/cryptos
│   ├── welcome.py       # Mensajes de bienvenida
│   └── xp.py            # 📈 Sistema de XP y niveles
├── utils/
│   ├── colors.py        # Paleta de colores fija
│   ├── database.py      # Base de datos SQLite
│   ├── embed_styles.py  # Estilos de embeds
│   └── ui.py            # Componentes UI (botones, paginación)
└── gifs/                # GIFs para comandos Mint
```

---

## 📦 Dependencias

```
discord.py[voice]>=2.3.0
yt-dlp>=2024.12.13
pynacl>=1.5.0
asyncio
aiohttp
Pillow>=10.0.0
requests>=2.0.0
ffmpeg-python
aiosqlite>=0.20.0
python-dotenv>=1.0.0
wavelink>=3.0.0
```

---

## 📜 Licencia

MIT

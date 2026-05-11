from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Muestra todos los comandos disponibles")
    async def comandos(self, ctx):
        """Ver todos los comandos disponibles"""
        from utils import ui

        embeds = [
            # Página 1: Música
            self._music_help(),
            # Página 2: Economía
            self._economy_help(),
            # Página 3: Casino
            self._casino_help(),
            # Página 4: Trading
            self._trading_help(),
            # Página 5: Diversión
            self._fun_help(),
            # Página 6: Interacción
            self._interaction_help(),
            # Página 7: Juegos
            self._games_help(),
            # Página 8: Perfil & XP
            self._profile_help(),
            # Página 9: Leaderboards
            self._leaderboards_help(),
            # Página 10: Información
            self._info_help(),
            # Página 11: Moderación
            self._moderation_help(),
            # Página 12: Configuración
            self._config_help(),
            # Página 13: Admin
            self._admin_help(),
        ]

        view = ui.PaginatorView(embeds)
        await ctx.send(embed=embeds[0], view=view)

    # ─── PÁGINA 1: MÚSICA ───────────────────────────────────────────────
    def _music_help(self):
        embed = discord.Embed(
            title="🎵 COMANDOS DE MÚSICA",
            color=discord.Color.blue(),
            description="Reproduce música desde YouTube, Spotify y Apple Music"
        )
        embed.add_field(name="/play <canción>", value="Reproduce una canción desde YouTube", inline=False)
        embed.add_field(name="&pause", value="Pausa la canción actual", inline=False)
        embed.add_field(name="&resume", value="Reanuda la canción pausada", inline=False)
        embed.add_field(name="&skip", value="Salta a la siguiente canción", inline=False)
        embed.add_field(name="&stop", value="Detiene la reproducción", inline=False)
        embed.add_field(name="&queue", value="Muestra la cola de canciones", inline=False)
        embed.add_field(name="&nowplaying / /np", value="Muestra la canción actual", inline=False)
        embed.add_field(name="&loop", value="Activa/desactiva el loop", inline=False)
        embed.add_field(name="&shuffle", value="Mezcla la cola de reproducción", inline=False)
        embed.add_field(name="&volume <0-100>", value="Ajusta el volumen", inline=False)
        embed.add_field(name="&disconnect / &leave", value="Desconecta el bot del canal de voz", inline=False)
        return embed

    # ─── PÁGINA 2: ECONOMÍA ─────────────────────────────────────────────
    def _economy_help(self):
        embed = discord.Embed(
            title="💰 COMANDOS DE ECONOMÍA",
            color=discord.Color.gold(),
            description="Gana, gasta y gestiona tus coins. Todos los comandos funcionan con / y &"
        )
        embed.add_field(name="/balance [usuario]", value="Ve tu balance de coins y banco", inline=False)
        embed.add_field(name="/daily", value="Recibe 500 coins cada 24 horas", inline=False)
        embed.add_field(name="/weekly", value="Recibe 2000 coins cada 7 días", inline=False)
        embed.add_field(name="/work", value="Trabaja y gana 50-200 coins (cooldown 3s, 25x/día)", inline=False)
        embed.add_field(name="/deposit <monto>", value="Deposita coins en tu banco (seguro)", inline=False)
        embed.add_field(name="/withdraw <monto>", value="Retira coins de tu banco", inline=False)
        embed.add_field(name="/bank", value="Ve el estado de tu banco", inline=False)
        embed.add_field(name="/gamble <monto>", value="Apuesta coins (50% ganar, 50% perder)", inline=False)
        embed.add_field(name="/pagar <usuario> <monto>", value="Transfiere coins a otro usuario", inline=False)
        embed.add_field(name="/leaderboard coins", value="Top 10 usuarios más ricos", inline=False)
        return embed

    # ─── PÁGINA 3: CASINO ──────────────────────────────────────────────
    def _casino_help(self):
        embed = discord.Embed(
            title="🎰 COMANDOS DE CASINO",
            color=discord.Color.brand_green(),
            description="Juegos de azar para apostar tus coins y multiplicarlos"
        )
        embed.add_field(name="/slots [monto] [grilla]", value="Tragamonedas 3×3, 5×3 o 7×3. Multiplica tu apuesta hasta 10×", inline=False)
        embed.add_field(name="/crash <monto>", value="Juego Crash: retira antes de que explote. Multiplicador creciente", inline=False)
        embed.add_field(name="/mines <monto> [grid]", value="Buscaminas: elige casillas y evita las minas (3×3 a 7×7)", inline=False)
        embed.add_field(name="/plinko <monto> [riesgo]", value="Plinko: suelta una ficha y gana según la casilla (bajo/medio/alto riesgo)", inline=False)
        embed.add_field(name="/dice <monto> [cara]", value="Dados: apuesta a un número (1-6) o superior/inferior. Paga 2× a 6×", inline=False)
        embed.add_field(name="/casino-stats [usuario]", value="Estadísticas del casino: rachas, ganancias, pérdidas", inline=False)
        return embed

    # ─── PÁGINA 4: TRADING ─────────────────────────────────────────────
    def _trading_help(self):
        embed = discord.Embed(
            title="📊 COMANDOS DE TRADING",
            color=discord.Color.orange(),
            description="Invierte en el mercado de acciones y cryptos. Usa coins para comprar/vender"
        )
        embed.add_field(name="/stocks", value="Muestra el mercado disponible (crypto + acciones)", inline=False)
        embed.add_field(name="/buy <símbolo> <cantidad>", value="Compra acciones de una empresa/crypto", inline=False)
        embed.add_field(name="/sell <símbolo> <cantidad>", value="Vende tus acciones", inline=False)
        embed.add_field(name="/portfolio", value="Muestra tu cartera de inversiones", inline=False)
        embed.add_field(name="/stonks", value="Precios en vivo del mercado", inline=False)
        embed.add_field(name="/price <símbolo>", value="Precio actual de un activo", inline=False)
        return embed

    # ─── PÁGINA 5: DIVERSIÓN ───────────────────────────────────────────
    def _fun_help(self):
        embed = discord.Embed(
            title="🎮 COMANDOS DE DIVERSIÓN",
            color=discord.Color.purple(),
            description="Juega, ríe y diviértete con estos comandos"
        )
        embed.add_field(name="/8ball <pregunta>", value="La bola mágica responde tu pregunta", inline=False)
        embed.add_field(name="/coinflip", value="Lanza una moneda (Cara/Cruz)", inline=False)
        embed.add_field(name="/dice [caras]", value="Lanza un dado (por defecto 6 caras)", inline=False)
        embed.add_field(name="/choose op1 | op2 | ...", value="Elige entre las opciones que das", inline=False)
        embed.add_field(name="/howgay [usuario]", value="Mide qué tan gay eres 😏", inline=False)
        embed.add_field(name="/lovecalc [usuario1] [usuario2]", value="Calcula el amor entre dos personas", inline=False)
        embed.add_field(name="/ascii <texto>", value="Convierte texto a ASCII art", inline=False)
        embed.add_field(name="/reverse <texto>", value="Invierte un texto", inline=False)
        embed.add_field(name="/bigtext <texto>", value="Convierte texto a letras grandes emoji", inline=False)
        embed.add_field(name="/owoify <texto>", value="Convierte texto a OwO", inline=False)
        embed.add_field(name="/meme [subreddit]", value="Obtén un meme aleatorio de Reddit", inline=False)
        embed.add_field(name="/waifu / /nekogirl", value="Imagen aleatoria de waifu/neko", inline=False)
        embed.add_field(name="/trivia [tema]", value="Responde preguntas de cultura general", inline=False)
        embed.add_field(name="/randomnumber [min] [max]", value="Número aleatorio entre dos valores", inline=False)
        return embed

    # ─── PÁGINA 6: INTERACCIÓN SOCIAL ──────────────────────────────────
    def _interaction_help(self):
        embed = discord.Embed(
            title="🤗 COMANDOS DE INTERACCIÓN",
            color=discord.Color.magenta(),
            description="Interactúa con otros usuarios usando GIFs animados de anime"
        )
        embed.add_field(name="/hug <usuario>", value="Abraza a alguien", inline=False)
        embed.add_field(name="/kiss <usuario>", value="Besa a alguien", inline=False)
        embed.add_field(name="/pat <usuario>", value="Acaricia a alguien", inline=False)
        embed.add_field(name="/slap <usuario>", value="Abofetea a alguien", inline=False)
        embed.add_field(name="/cuddle <usuario>", value="Acurrúcate con alguien", inline=False)
        embed.add_field(name="/bonk <usuario>", value="Golpea a alguien en la cabeza", inline=False)
        embed.add_field(name="/bite <usuario>", value="Muerde a alguien", inline=False)
        embed.add_field(name="/punch <usuario>", value="Golpea a alguien", inline=False)
        embed.add_field(name="/dance", value="Baila solo o con alguien", inline=False)
        embed.add_field(name="/blurp <usuario>", value="Hazle burla a alguien", inline=False)
        return embed

    # ─── PÁGINA 7: JUEGOS MULTIJUGADOR ─────────────────────────────────
    def _games_help(self):
        embed = discord.Embed(
            title="🎲 JUEGOS MULTIJUGADOR",
            color=discord.Color.teal(),
            description="Juegos interactivos para jugar con otros usuarios"
        )
        embed.add_field(name="/snake @usuario", value="Juego de la serpiente: compite por la puntuación más alta", inline=False)
        embed.add_field(name="/connect4 @usuario", value="Conecta 4: el primero en alinear 4 fichas gana", inline=False)
        embed.add_field(name="/tictactoe @usuario", value="Tres en raya: el clásico juego de estrategia", inline=False)
        embed.add_field(name="/rps @usuario", value="Piedra, Papel o Tijera contra otro usuario", inline=False)
        return embed

    # ─── PÁGINA 8: PERFIL & XP ──────────────────────────────────────────
    def _profile_help(self):
        embed = discord.Embed(
            title="👤 COMANDOS DE PERFIL Y NIVELES",
            color=discord.Color.pink(),
            description="Personaliza tu perfil y sube de nivel"
        )
        embed.add_field(name="/perfil [usuario]", value="Ve tu perfil o el de otro con stats, nivel, coins, etc.", inline=False)
        embed.add_field(name="/bio <texto>", value="Establece tu biografía (máx 100 caracteres)", inline=False)
        embed.add_field(name="/level / /rank [usuario]", value="Muestra tu nivel y XP actual", inline=False)
        embed.add_field(name="/marry <usuario>", value="Propón matrimonio a otro usuario", inline=False)
        embed.add_field(name="/divorce", value="Divórciate de tu pareja actual", inline=False)
        embed.add_field(name="/leaderboard xp", value="Top 10 usuarios por experiencia", inline=False)
        embed.add_field(name="/leaderboard marriage", value="Ver todas las parejas registradas", inline=False)
        return embed

    # ─── PÁGINA 9: LEADERBOARDS ────────────────────────────────────────
    def _leaderboards_help(self):
        embed = discord.Embed(
            title="🏆 LEADERBOARDS (RANKINGS)",
            color=discord.Color.orange(),
            description="Rankings globales del servidor"
        )
        embed.add_field(name="/leaderboard coins", value="Top 10 usuarios más ricos", inline=False)
        embed.add_field(name="/leaderboard xp", value="Top 10 usuarios por experiencia", inline=False)
        embed.add_field(name="/leaderboard marriage", value="Ver todas las parejas registradas", inline=False)
        embed.add_field(name="/leaderboard casino", value="Top 10 del casino (más ganancias)", inline=False)
        embed.add_field(name="/leaderboard trading", value="Top 10 del mercado de valores", inline=False)
        return embed

    # ─── PÁGINA 10: INFORMACIÓN ────────────────────────────────────────
    def _info_help(self):
        embed = discord.Embed(
            title="ℹ️ COMANDOS DE INFORMACIÓN",
            color=discord.Color.blurple(),
            description="Comandos útiles para obtener información"
        )
        embed.add_field(name="/ping", value="Muestra la latencia del bot", inline=False)
        embed.add_field(name="/avatar [usuario]", value="Muestra el avatar de un usuario en grande", inline=False)
        embed.add_field(name="/banner [usuario]", value="Muestra el banner de perfil de un usuario", inline=False)
        embed.add_field(name="/serverinfo", value="Información detallada del servidor", inline=False)
        embed.add_field(name="/userinfo [usuario]", value="Información detallada de un usuario", inline=False)
        embed.add_field(name="/roleinfo <rol>", value="Información de un rol específico", inline=False)
        embed.add_field(name="/channelinfo [#canal]", value="Información de un canal", inline=False)
        embed.add_field(name="/servericon", value="Muestra el icono del servidor en grande", inline=False)
        embed.add_field(name="/botinfo", value="Información sobre Mint Bot", inline=False)
        embed.add_field(name="/invite", value="Invita a Mint Bot a tu servidor", inline=False)
        embed.add_field(name="/comandos", value="Muestra esta lista de comandos (¡estás aquí!)", inline=False)
        return embed

    # ─── PÁGINA 11: MODERACIÓN ─────────────────────────────────────────
    def _moderation_help(self):
        embed = discord.Embed(
            title="🛡️ COMANDOS DE MODERACIÓN",
            color=discord.Color.red(),
            description="Modera tu servidor (requiere permisos adecuados)"
        )
        embed.add_field(name="/warn <usuario> [razón]", value="Advierte a un usuario (3 warns = kick automático)", inline=False)
        embed.add_field(name="/warns [usuario]", value="Lista las advertencias de un usuario", inline=False)
        embed.add_field(name="/clearwarns <usuario>", value="Limpia todas las advertencias de un usuario", inline=False)
        embed.add_field(name="/kick <usuario> [razón]", value="Expulsa a un usuario del servidor", inline=False)
        embed.add_field(name="/ban <usuario> [razón]", value="Banea a un usuario del servidor", inline=False)
        embed.add_field(name="/unban <id> [razón]", value="Desbanea a un usuario (por ID)", inline=False)
        embed.add_field(name="/tempban <usuario> <días> [razón]", value="Baneo temporal por días", inline=False)
        embed.add_field(name="/mute <usuario> <minutos> [razón]", value="Silencia a un usuario temporalmente", inline=False)
        embed.add_field(name="/unmute <usuario>", value="Quita el silencio a un usuario", inline=False)
        embed.add_field(name="/timeout <usuario> <minutos> [razón]", value="Timeout (silencio completo) por tiempo", inline=False)
        embed.add_field(name="/untimeout <usuario>", value="Quita el timeout", inline=False)
        embed.add_field(name="/slowmode <segundos>", value="Establece modo lento en el canal actual", inline=False)
        embed.add_field(name="/lock [#canal]", value="Bloquea un canal (solo admins pueden hablar)", inline=False)
        embed.add_field(name="/unlock [#canal]", value="Desbloquea un canal", inline=False)
        embed.add_field(name="/clear [cantidad]", value="Elimina mensajes en masa (máx 100)", inline=False)
        embed.add_field(name="/snipe", value="Muestra el último mensaje eliminado", inline=False)
        embed.add_field(name="/esnipe", value="Muestra el último mensaje editado", inline=False)
        embed.add_field(name="/voicekick <usuario>", value="Expulsa a un usuario del canal de voz", inline=False)
        embed.add_field(name="/voicemove <usuario> <canal>", value="Mueve a un usuario a otro canal de voz", inline=False)
        embed.add_field(name="/vcmute <usuario>", value="Silencia a un usuario en el canal de voz", inline=False)
        embed.add_field(name="/vcunmute <usuario>", value="Quita el silencio de voz", inline=False)
        return embed

    # ─── PÁGINA 12: CONFIGURACIÓN ───────────────────────────────────────
    def _config_help(self):
        embed = discord.Embed(
            title="⚙️ COMANDOS DE CONFIGURACIÓN",
            color=discord.Color.dark_blue(),
            description="Configura el comportamiento del bot en tu servidor"
        )
        embed.add_field(name="/dashboard", value="Panel de configuración de bienvenidas (canal, mensaje, embed)", inline=False)
        embed.add_field(name="/testwelcome", value="Prueba el mensaje de bienvenida configurado", inline=False)
        embed.add_field(name="/antilinks [on/off]", value="Activa/desactiva el bloqueo de enlaces", inline=False)
        embed.add_field(name="/blacklist add/remove/list <palabra>", value="Gestiona la lista de palabras prohibidas", inline=False)
        embed.add_field(name="/autorole add/remove/list <rol>", value="Configura roles automáticos al unirse", inline=False)
        embed.add_field(name="/prefix [nuevo_prefix]", value="Cambia el prefix del bot en este servidor", inline=False)
        embed.add_field(name="/creacolores", value="Crea los 30 roles de colores para el servidor", inline=False)
        embed.add_field(name="/autorroles", value="Muestra el menú interactivo para elegir color", inline=False)
        return embed

    # ─── PÁGINA 13: ADMIN ──────────────────────────────────────────────
    def _admin_help(self):
        embed = discord.Embed(
            title="🔧 COMANDOS DE ADMIN (OWNER)",
            color=discord.Color.dark_red(),
            description="Solo para el dueño del bot. Comandos de control y gestión"
        )
        embed.add_field(name="/reload <cog>", value="Recarga un módulo (cog) del bot sin reiniciar", inline=False)
        embed.add_field(name="/load <cog>", value="Carga un nuevo cog", inline=False)
        embed.add_field(name="/unload <cog>", value="Descarga un cog", inline=False)
        embed.add_field(name="/sync", value="Sincroniza los slash commands con Discord", inline=False)
        embed.add_field(name="/addcoins <usuario> <monto>", value="Agrega coins a un usuario (admin only)", inline=False)
        embed.add_field(name="/removecoins <usuario> <monto>", value="Quita coins a un usuario", inline=False)
        embed.add_field(name="/setlevel <usuario> <nivel>", value="Establece el nivel de un usuario", inline=False)
        embed.add_field(name="/serverlist", value="Lista los servidores donde está el bot", inline=False)
        embed.add_field(name="/botstatus <texto>", value="Cambia el estado (playing/watching/listening) del bot", inline=False)
        return embed

async def setup(bot):
    await bot.add_cog(Help(bot))

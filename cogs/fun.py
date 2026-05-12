from discord.ext import commands
import discord
import random
import aiohttp
from utils import ui

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(description="Pregunta a la bola mágica")
    async def eightball(self, ctx, *, question: str):
        """Bola 8 mágica - &eightball <pregunta>"""
        responses = [
            "Sí, definitivamente",
            "No, de ninguna manera",
            "Puede ser",
            "Pregunta de nuevo más tarde",
            "La respuesta es clara",
            "No cuentes con ello",
            "Seguramente",
            "Muy dudoso",
            "Sin duda",
            "El futuro es incierto"
        ]
        
        embed = ui.simple_embed(
            title="🔮 Bola Mágica",
            description=f"**Pregunta:** {question}\n\n**Respuesta:** {random.choice(responses)}",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(description="Juega a la ruleta rusa (50% probabilidad)")
    async def roulette(self, ctx):
        """Ruleta rusa - 50% de perder dinero (necesita cog economy)"""
        economy = self.bot.get_cog('Economy')
        if not economy:
            await ctx.send(embed=ui.error_embed("Economy cog no encontrado"))
            return

        balance = economy.get_balance(ctx.author.id)

        if balance == 0:
            await ctx.send(embed=ui.error_embed("Necesitas dinero para jugar"))
            return

        if random.random() > 0.5:
            loss = int(balance * 0.5)
            economy.add_money(ctx.author.id, -loss)
            await ctx.send(embed=ui.simple_embed("💀 ¡PERDISTE!", f"Perdiste **{loss}** coins", color=discord.Color.red()))
        else:
            gain = int(balance * 0.5)
            economy.add_money(ctx.author.id, gain)
            await ctx.send(embed=ui.success_embed(f"¡SOBREVIVISTE! Ganaste **{gain}** coins por tu valentía"))
    
    @commands.hybrid_command(description="Responde una pregunta de trivia")
    async def trivia(self, ctx):
        """Pregunta de trivia aleatoria"""
        questions = [
            {"q": "¿Cuál es el planeta más grande del sistema solar?", "a": "jupiter"},
            {"q": "¿En qué año se inventó el internet?", "a": "1969"},
            {"q": "¿Cuál es la capital de Francia?", "a": "paris"},
            {"q": "¿Cuántos continentes hay?", "a": "7"},
            {"q": "¿En qué país se originó el tango?", "a": "argentina"},
            {"q": "¿Cuál es el río más largo del mundo?", "a": "nilo"},
            {"q": "¿En qué año cayó el Muro de Berlín?", "a": "1989"},
            {"q": "¿Cuántos lados tiene un hexágono?", "a": "6"},
            # Nuevas preguntas
            {"q": "¿Cuál es el videojuego más vendido de la historia?", "a": "minecraft"},
            {"q": "¿Quién escribió Romeo y Julieta?", "a": "shakespeare"},
            {"q": "¿Cuál es el símbolo químico del oro?", "a": "au"},
            {"q": "¿Cuántos jugadores hay en un equipo de fútbol?", "a": "11"},
            {"q": "¿Cuál es la capital de Japón?", "a": "tokyo"},
            {"q": "¿Quién es el protagonista de The Legend of Zelda?", "a": "link"},
            {"q": "¿Qué número sigue después de 3.14 en Pi?", "a": "15"},
            {"q": "¿Cuál es el animal terrestre más rápido?", "a": "guepardo"},
            {"q": "¿Qué planeta es conocido como el Planeta Rojo?", "a": "marte"},
            {"q": "¿Cómo se llama el hermano de Mario?", "a": "luigi"},
            {"q": "¿Qué compañía creó el iPhone?", "a": "apple"},
            {"q": "¿Quién pintó la Mona Lisa?", "a": "da vinci"},
            {"q": "¿En qué año llegó el hombre a la luna?", "a": "1969"},
        ]
        
        question = random.choice(questions)
        embed = ui.info_embed("🧠 Trivia", question["q"])
        
        await ctx.send(embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=10)
            if answer.content.lower() == question["a"]:
                await ctx.send(embed=ui.success_embed(f"¡Correcto! La respuesta era **{question['a']}**"))
            else:
                await ctx.send(embed=ui.error_embed(f"Incorrecto. La respuesta era **{question['a']}**"))
        except:
            await ctx.send(embed=ui.info_embed("⏱️ Tiempo Agotado", f"La respuesta era **{question['a']}**"))
    
    @commands.hybrid_command(description="Obtén un meme aleatorio de Reddit")
    async def meme(self, ctx):
        """Obtener meme aleatorio de Reddit"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://meme-api.com/gimme') as r:
                    if r.status != 200:
                         await ctx.send(embed=ui.error_embed("No se pudo obtener el meme"))
                         return
                    data = await r.json()
                    
                    embed = ui.simple_embed(
                        title=data['title'],
                        description="",
                        image_url=data['url'],
                        footer_text=f"👍 {data['ups']} | r/{data['subreddit']}"
                    )
                    await ctx.send(embed=embed)
        except Exception:
                     await ctx.send(embed=ui.error_embed("Error al conectar con la API de memes"))

    @commands.hybrid_command(description="Lanza una moneda")
    async def flip(self, ctx):
        """Lanzar una moneda"""
        result = random.choice(['Cara ✅', 'Cruz ❌'])
        await ctx.send(embed=ui.simple_embed("🪙 Moneda", f"Resultado: **{result}**"))

    @commands.hybrid_command(description="Lanza un dado")
    async def roll(self, ctx, sides: int = 6):
        """Lanzar dado - &roll <caras>"""
        if sides < 2:
            await ctx.send(embed=ui.error_embed("El dado debe tener al menos 2 caras"))
            return

        result = random.randint(1, sides)
        await ctx.send(embed=ui.simple_embed("🎲 Dado", f"Sacaste un **{result}** en un dado de {sides} caras"))

    @commands.hybrid_command(description="Elige entre varias opciones")
    async def choose(self, ctx, *, options: str):
        """Elegir entre opciones - &choose opción1 | opción2 | opción3"""
        choices = [c.strip() for c in options.split('|')]

        if len(choices) < 2:
            await ctx.send(embed=ui.error_embed("Necesitas al menos 2 opciones separadas por |"))
            return

        chosen = random.choice(choices)
        await ctx.send(embed=ui.success_embed(f"Elegí: **{chosen}**"))

    @commands.hybrid_command(
        name="howgay",
        description="🏳️‍🌈 Mide qué tan gay eres (o alguien más)",
    )
    async def howgay(self, ctx, usuario: discord.Member = None):
        """Mide el nivel de gay de un usuario"""
        usuario = usuario or ctx.author
        if usuario.id == ctx.author.id:
            desc = f"**{usuario.display_name}** es **{random.randint(0,100)}%** gay 🏳️‍🌈"
        else:
            desc = f"**{usuario.display_name}** es **{random.randint(0,100)}%** gay 🏳️‍🌈\n(según {ctx.author.display_name})"
        await ctx.send(embed=ui.simple_embed("🏳️‍🌈 Medidor de Gay", desc))

    @commands.hybrid_command(
        name="lovecalc",
        description="💕 Calcula el amor entre dos personas",
    )
    async def lovecalc(self, ctx, persona1: discord.Member, persona2: discord.Member = None):
        """Calcula la compatibilidad amorosa"""
        if persona2 is None:
            persona2 = ctx.author
        love = random.randint(0, 100)
        hearts = "❤️" * (love // 10) + "🖤" * (10 - love // 10)
        desc = f"**{persona1.display_name}** 💕 **{persona2.display_name}**\n\n{hearts}\n**{love}%** de compatibilidad"
        if love >= 80:
            desc += "\n✨ ¡Destinados a estar juntos!"
        elif love >= 50:
            desc += "\n💫 Tienen potencial"
        else:
            desc += "\n💔 Mejor como amigos"
        await ctx.send(embed=ui.simple_embed("💕 LoveCalc", desc))

    @commands.hybrid_command(
        name="ascii",
        description="🎨 Convierte texto a ASCII art",
    )
    async def ascii(self, ctx, *, texto: str):
        """Convierte texto a arte ASCII (letras grandes)"""
        if len(texto) > 20:
            await ctx.send(embed=ui.error_embed("El texto no puede tener más de **20** caracteres"))
            return
        letras = {
            'a':' ▄▀ ',' b':' ▄▄ ',' c':' ▄▄ ',' d':' ▄▀ ',' e':' ▄▄ ',' f':' ▄▄ ',' g':' ▄▄ ',' h':' ▄ ▄ ',' i':' ▄▄ ',' j':' ▄▄ ',' k':' ▄ ▄ ',' l':' ▄   ',' m':' ▄▄▄ ',' n':' ▄▄▄ ',' o':' ▄▄▄ ',' p':' ▄▄▄ ',' q':' ▄▄▄ ',' r':' ▄▄▄ ',' s':' ▄▄▄ ',' t':' ▄▄▄▄',' u':' ▄ ▄ ',' v':' ▄ ▄ ',' w':' ▄ ▄▄▄',' x':' ▄ ▄ ',' y':' ▄ ▄▄▄',' z':' ▄▄▄ ',
            'A':'█▀█ ','B':'█▀▄ ','C':'█▀▀ ','D':'█▀▄ ','E':'█▀▀ ','F':'█▀▀ ','G':'█▀▀ ','H':'█ █ ','I':'██ ','J':' ██ ','K':'█▄▀ ','L':'█   ','M':'█▄▄▄█','N':'█▄▄█ ','O':'█▄▄█ ','P':'█▀▄ ','Q':'█▄▄▄','R':'█▀▄ ','S':'█▄▄ ','T':'▀█▀ ','U':'█ █ ','V':'█ █ ','W':'█ ██▄','X':'▀▄▀ ','Y':'█ █ ','Z':'▀▀█ '
        }
        resultado = []
        texto = texto.lower()
        for char in texto:
            if char in letras:
                resultado.append(letras[char])
            elif char == ' ':
                resultado.append('    ')
            else:
                resultado.append(f' {char} ')
        await ctx.send(f"```\n{' '.join(resultado)}\n```")

    @commands.hybrid_command(
        name="reverse",
        description="🔄 Invierte un texto",
    )
    async def reverse(self, ctx, *, texto: str):
        """Invierte el texto que escribas"""
        invertido = texto[::-1]
        if len(invertido) > 1000:
            await ctx.send(embed=ui.error_embed("El texto es muy largo para invertir"))
            return
        await ctx.send(embed=ui.simple_embed("🔄 Texto invertido", f"**Original:** {texto}\n**Invertido:** {invertido}"))

    @commands.hybrid_command(
        name="bigtext",
        description="🔤 Convierte texto a letras grandes con emojis",
    )
    async def bigtext(self, ctx, *, texto: str):
        """Texto a letras emoji"""
        letras = {
            'a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩', 'e': '🇪', 'f': '🇫', 'g': '🇬',
            'h': '🇭', 'i': '🇮', 'j': '🇯', 'k': '🇰', 'l': '🇱', 'm': '🇲', 'n': '🇳',
            'o': '🇴', 'p': '🇵', 'q': '🇶', 'r': '🇷', 's': '🇸', 't': '🇹', 'u': '🇺',
            'v': '🇻', 'w': '🇼', 'x': '🇽', 'y': '🇾', 'z': '🇿', ' ': '  ',
            '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
            '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣',
        }
        if len(texto) > 30:
            await ctx.send(embed=ui.error_embed("Texto muy largo (máx 30 caracteres)"))
            return
        resultado = []
        for char in texto.lower():
            resultado.append(letras.get(char, char))
        await ctx.send(' '.join(resultado))

    @commands.hybrid_command(
        name="owoify",
        description="😺 Convierte texto a lenguaje OwO",
    )
    async def owoify(self, ctx, *, texto: str):
        """OwO what's this?"""
        owotext = texto
        owotext = owotext.replace('r', 'w').replace('l', 'w')
        owotext = owotext.replace('R', 'W').replace('L', 'W')
        owotext = owotext.replace('v', 'w').replace('V', 'W')
        owotext = owotext.replace('ñ', 'ny').replace('Ñ', 'Ny')
        owotext = random.choice(["OwO ", "*nuzzles* ", "*pounces* ", "*notices* "]) + owotext
        owotext += " " + random.choice(["*w*", "UwU", ">w<", ":3", "^w^", "rawr"])
        if len(owotext) > 2000:
            owotext = owotext[:1997] + "..."
        await ctx.send(owotext)

    @commands.hybrid_command(
        name="waifu",
        description="🖼️ Muestra una waifu anime aleatoria",
    )
    async def waifu(self, ctx):
        """Obtén una imagen waifu aleatoria"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.waifu.pics/sfw/waifu') as r:
                    if r.status == 200:
                        data = await r.json()
                        embed = ui.simple_embed(
                            title="🖼️ Waifu",
                            image_url=data['url'],
                            footer_text="waifu.pics"
                        )
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(embed=ui.error_embed("No se pudo obtener la waifu"))
        except:
            await ctx.send(embed=ui.error_embed("Error al conectar con la API"))

    @commands.hybrid_command(
        name="nekogirl",
        aliases=["neko", "nekogirl"],
        description="😺 Muestra una imagen neko aleatoria",
    )
    async def nekogirl(self, ctx):
        """Obtén una imagen neko aleatoria"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.waifu.pics/sfw/neko') as r:
                    if r.status == 200:
                        data = await r.json()
                        embed = ui.simple_embed(
                            title="😺 Neko girl",
                            image_url=data['url'],
                            footer_text="waifu.pics"
                        )
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(embed=ui.error_embed("No se pudo obtener la neko"))
        except:
            await ctx.send(embed=ui.error_embed("Error al conectar con la API"))

    @commands.hybrid_command(
        name="randomnumber",
        aliases=["rand"],
        description="🔢 Número aleatorio entre dos valores",
    )
    async def randomnumber(self, ctx, minimo: int = 1, maximo: int = 100):
        """Genera un número aleatorio entre mínimo y máximo"""
        if minimo >= maximo:
            await ctx.send(embed=ui.error_embed("El **mínimo** debe ser menor que el **máximo**"))
            return
        if maximo - minimo > 1000000:
            await ctx.send(embed=ui.error_embed("El rango máximo es de **1,000,000**"))
            return
        resultado = random.randint(minimo, maximo)
        await ctx.send(embed=ui.simple_embed("🔢 Número Aleatorio", f"Entre **{minimo}** y **{maximo}**\n\n🎯 **{resultado}**"))

async def setup(bot):
    if bot.get_cog("Fun") is not None:
        return
    await bot.add_cog(Fun(bot))

import discord
from discord.ext import commands
from discord import app_commands
import json, os, random, aiohttp
from utils.ui import error_embed, success_embed, info_embed

# ─── GAMES ───

class TicTacToeButton(discord.ui.Button):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        super().__init__(style=discord.ButtonStyle.secondary, label="⬜", row=row)

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        if interaction.user.id not in (view.player1.id, view.player2.id):
            await interaction.response.send_message("❌ No eres parte de esta partida", ephemeral=True)
            return
        if interaction.user.id != view.current_player.id:
            await interaction.response.send_message("⏳ No es tu turno", ephemeral=True)
            return
        if view.board[self.row][self.col] is not None:
            await interaction.response.send_message("❌ Esa casilla ya está ocupada", ephemeral=True)
            return

        symbol = "❌" if view.current_player == view.player1 else "⭕"
        self.label = symbol
        self.disabled = True
        if symbol == "❌":
            self.style = discord.ButtonStyle.danger
        else:
            self.style = discord.ButtonStyle.primary

        view.board[self.row][self.col] = symbol
        winner = view.check_winner()

        if winner:
            for child in view.children:
                child.disabled = True
            if winner == "empate":
                embed = discord.Embed(title="🤝 Empate!", color=discord.Color.gold())
            else:
                ganador = view.player1 if winner == "❌" else view.player2
                embed = discord.Embed(title=f"🎉 {ganador.display_name} ganó!", color=discord.Color.green())
            await interaction.response.edit_message(view=view, embed=embed)
            view.stop()
            return

        view.current_player = view.player2 if view.current_player == view.player1 else view.player1
        turno = view.current_player.mention
        embed = discord.Embed(title="🎮 Tres en Raya", description=f"Turno de {turno}", color=discord.Color.blurple())
        await interaction.response.edit_message(view=view, embed=embed)


class TicTacToeView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=120)
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[None, None, None] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.add_item(TicTacToeButton(r, c))

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] and self.board[i][0]:
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] and self.board[0][i]:
                return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0]:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2]:
            return self.board[0][2]
        if all(all(cell is not None for cell in row) for row in self.board):
            return "empate"
        return None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self, embed=discord.Embed(title="⏰ Tiempo agotado", color=discord.Color.red()))
        except:
            pass


class Connect4Button(discord.ui.Button):
    def __init__(self, col):
        self.col = col
        super().__init__(style=discord.ButtonStyle.secondary, label=f"⬇️", row=0)

    async def callback(self, interaction: discord.Interaction):
        view: Connect4View = self.view
        if interaction.user.id not in (view.player1.id, view.player2.id):
            await interaction.response.send_message("❌ No eres parte de esta partida", ephemeral=True)
            return
        if interaction.user.id != view.current_player.id:
            await interaction.response.send_message("⏳ No es tu turno", ephemeral=True)
            return

        # Find lowest empty row in this column
        for row in range(5, -1, -1):
            if view.board[row][self.col] is None:
                symbol = "🔴" if view.current_player == view.player1 else "🟡"
                view.board[row][self.col] = symbol
                break
        else:
            await interaction.response.send_message("❌ Columna llena", ephemeral=True)
            return

        winner = view.check_winner()
        if winner:
            for child in view.children:
                child.disabled = True
            if winner == "empate":
                embed = discord.Embed(title="🤝 Empate!", color=discord.Color.gold())
            else:
                ganador = view.player1 if winner == "🔴" else view.player2
                embed = discord.Embed(title=f"🎉 {ganador.display_name} ganó!", color=discord.Color.green())
            await interaction.response.edit_message(view=view, embed=embed)
            view.stop()
            return

        view.current_player = view.player2 if view.current_player == view.player1 else view.player1
        embed = discord.Embed(title="🟡 Conecta 4 🔴", description=f"Turno de {view.current_player.mention}", color=discord.Color.blurple())
        await interaction.response.edit_message(view=view, embed=embed)


class Connect4View(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=120)
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[None for _ in range(7)] for _ in range(6)]
        for c in range(7):
            self.add_item(Connect4Button(c))

    def check_winner(self):
        # Horizontal
        for r in range(6):
            for c in range(4):
                if self.board[r][c] and self.board[r][c] == self.board[r][c+1] == self.board[r][c+2] == self.board[r][c+3]:
                    return self.board[r][c]
        # Vertical
        for r in range(3):
            for c in range(7):
                if self.board[r][c] and self.board[r][c] == self.board[r+1][c] == self.board[r+2][c] == self.board[r+3][c]:
                    return self.board[r][c]
        # Diagonal \
        for r in range(3):
            for c in range(4):
                if self.board[r][c] and self.board[r][c] == self.board[r+1][c+1] == self.board[r+2][c+2] == self.board[r+3][c+3]:
                    return self.board[r][c]
        # Diagonal /
        for r in range(3, 6):
            for c in range(4):
                if self.board[r][c] and self.board[r][c] == self.board[r-1][c+1] == self.board[r-2][c+2] == self.board[r-3][c+3]:
                    return self.board[r][c]
        if all(all(cell is not None for cell in row) for row in self.board):
            return "empate"
        return None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self, embed=discord.Embed(title="⏰ Tiempo agotado", color=discord.Color.red()))
        except:
            pass


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="tictactoe", aliases=["ttt"], description="Juega Tres en Raya contra otro usuario")
    @app_commands.describe(usuario="Contrincante")
    async def tictactoe(self, ctx, usuario: discord.Member):
        if usuario.id == ctx.author.id:
            await ctx.send(embed=error_embed("❌ No puedes jugar contra ti mismo"), ephemeral=True)
            return
        if usuario.bot:
            await ctx.send(embed=error_embed("❌ No puedes jugar contra un bot (aún)"), ephemeral=True)
            return
        view = TicTacToeView(ctx.author, usuario)
        embed = discord.Embed(title="🎮 Tres en Raya", description=f"Turno de {ctx.author.mention}", color=discord.Color.blurple())
        await ctx.send(f"{ctx.author.mention} vs {usuario.mention}", embed=embed, view=view)

    @commands.hybrid_command(name="connect4", aliases=["conecta4"], description="Juega Conecta 4 contra otro usuario")
    @app_commands.describe(usuario="Contrincante")
    async def connect4(self, ctx, usuario: discord.Member):
        if usuario.id == ctx.author.id:
            await ctx.send(embed=error_embed("❌ No puedes jugar contra ti mismo"), ephemeral=True)
            return
        if usuario.bot:
            await ctx.send(embed=error_embed("❌ No puedes jugar contra un bot (aún)"), ephemeral=True)
            return
        view = Connect4View(ctx.author, usuario)
        embed = discord.Embed(title="🟡 Conecta 4 🔴", description=f"Turno de {ctx.author.mention}", color=discord.Color.blurple())
        await ctx.send(f"{ctx.author.mention} vs {usuario.mention}", embed=embed, view=view)

    @commands.hybrid_command(name="rps", aliases=["ppt"], description="Piedra, Papel o Tijera contra otro usuario")
    @app_commands.describe(usuario="Contrincante")
    async def rps(self, ctx, usuario: discord.Member):
        if usuario.id == ctx.author.id:
            await ctx.send(embed=error_embed("❌ No puedes jugar contra ti mismo"), ephemeral=True)
            return
        if usuario.bot:
            await ctx.send(embed=error_embed("❌ No puedes jugar contra un bot (aún)"), ephemeral=True)
            return
        opciones = ["🪨 Piedra", "📄 Papel", "✂️ Tijera"]

        class RPSView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.p1_choice = None
                self.p2_choice = None
                self.p1_ready = False
                self.p2_ready = False

            @discord.ui.button(label="🪨 Piedra", style=discord.ButtonStyle.secondary)
            async def piedra(self, interaction, _):
                await self.handle(interaction, "piedra")

            @discord.ui.button(label="📄 Papel", style=discord.ButtonStyle.secondary)
            async def papel(self, interaction, _):
                await self.handle(interaction, "papel")

            @discord.ui.button(label="✂️ Tijera", style=discord.ButtonStyle.secondary)
            async def tijera(self, interaction, _):
                await self.handle(interaction, "tijera")

            async def handle(self, interaction, choice):
                if interaction.user.id == ctx.author.id:
                    self.p1_choice = choice
                    self.p1_ready = True
                elif interaction.user.id == usuario.id:
                    self.p2_choice = choice
                    self.p2_ready = True
                else:
                    await interaction.response.send_message("❌ No eres parte de esta partida", ephemeral=True)
                    return
                await interaction.response.defer()
                if self.p1_ready and self.p2_ready:
                    reglas = {"piedra": "tijera", "papel": "piedra", "tijera": "papel"}
                    if self.p1_choice == self.p2_choice:
                        resultado = "🤝 Empate!"
                    elif reglas[self.p1_choice] == self.p2_choice:
                        resultado = f"🎉 {ctx.author.mention} ganó!"
                    else:
                        resultado = f"🎉 {usuario.mention} ganó!"
                    embed = discord.Embed(title="📄🪨✂️ Resultado", color=discord.Color.green(), description=resultado)
                    embed.add_field(name=ctx.author.display_name, value=opciones[["piedra", "papel", "tijera"].index(self.p1_choice)])
                    embed.add_field(name=usuario.display_name, value=opciones[["piedra", "papel", "tijera"].index(self.p2_choice)])
                    for child in self.children:
                        child.disabled = True
                    await interaction.edit_original_response(embed=embed, view=self)
                    self.stop()
                else:
                    await interaction.edit_original_response(content=f"⏳ Esperando respuestas...")

        view = RPSView()
        embed = discord.Embed(title="📄🪨✂️ Piedra, Papel o Tijera", description=f"{ctx.author.mention} vs {usuario.mention}\nElige tu opción:", color=discord.Color.blurple())
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="trivia", description="Responde preguntas de trivia")
    async def trivia(self, ctx):
        await ctx.defer()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://opentdb.com/api.php?amount=1&type=multiple") as resp:
                    if resp.status != 200:
                        await ctx.send(embed=error_embed("❌ Error al obtener pregunta"), ephemeral=True)
                        return
                    data = await resp.json()
        except:
            await ctx.send(embed=error_embed("❌ Error de conexión con la API de trivia"), ephemeral=True)
            return

        if not data.get("results"):
            await ctx.send(embed=error_embed("❌ No se pudo obtener una pregunta"), ephemeral=True)
            return

        q = data["results"][0]
        import html
        pregunta = html.unescape(q["question"])
        correcta = html.unescape(q["correct_answer"])
        incorrectas = [html.unescape(i) for i in q["incorrect_answers"]]
        opciones = incorrectas + [correcta]
        random.shuffle(opciones)

        class TriviaView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.respondido = False

            async def send_response(self, interaction, selected, label):
                if self.respondido:
                    await interaction.response.send_message("⚠️ Ya respondiste!", ephemeral=True)
                    return
                self.respondido = True
                for child in self.children:
                    child.disabled = True
                if selected == correcta:
                    embed = discord.Embed(title="✅ Correcto!", description=f"**{pregunta}**\n\nRespuesta: {correcta}", color=discord.Color.green())
                else:
                    embed = discord.Embed(title="❌ Incorrecto", description=f"**{pregunta}**\n\nRespuesta correcta: **{correcta}**", color=discord.Color.red())
                await interaction.response.edit_message(embed=embed, view=self)
                self.stop()

        view = TriviaView()
        for op in opciones:
            btn = discord.ui.Button(label=op[:80], style=discord.ButtonStyle.secondary)
            async def callback(interaction, opcion=op):
                await view.send_response(interaction, opcion, "")
            btn.callback = callback
            view.add_item(btn)

        embed = discord.Embed(title=f"❓ Trivia — {html.unescape(q['category'])}", description=f"**{pregunta}**", color=discord.Color.blurple())
        embed.set_footer(text="Tienes 30 segundos")
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="meme", description="Muestra un meme aleatorio")
    async def meme(self, ctx):
        await ctx.defer()
        try:
            for subreddit in ["dankmemes", "memes", "ProgrammerHumor", "SpanishMeme"]:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://www.reddit.com/r/{subreddit}/hot.json?limit=50", headers={"User-Agent": "MintBot/1.0"}) as resp:
                        if resp.status != 200:
                            continue
                        data = await resp.json()
                        posts = [p["data"] for p in data.get("data", {}).get("children", [])
                                if not p["data"].get("stickied") and p["data"].get("url", "").endswith((".jpg", ".png", ".gif", ".jpeg"))]
                        if posts:
                            post = random.choice(posts)
                            embed = discord.Embed(title=post["title"], color=discord.Color.blurple())
                            embed.set_image(url=post["url"])
                            embed.set_footer(text=f"👍 {post.get('ups', 0)}  |  r/{subreddit}")
                            await ctx.send(embed=embed)
                            return
            await ctx.send(embed=error_embed("❌ No se encontraron memes"))
        except Exception as e:
            await ctx.send(embed=error_embed(f"❌ Error: {str(e)[:50]}"), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Games(bot))

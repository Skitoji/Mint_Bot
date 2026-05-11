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

    # ==================================================================
    # COMANDO: /snake
    # ==================================================================

    @commands.hybrid_command(
        name="snake",
        aliases=["serpiente"],
        description="🐍 Juego de la serpiente — atrapa la manzana y no choques",
    )
    async def snake(self, ctx: commands.Context) -> None:
        """🐍 Snake Game — Usa botones para dirigir la serpiente y comer manzanas."""
        # Tablero 8×8
        COLS, ROWS = 8, 8

        # Inicializar estado
        snake_body = [(3, 4), (3, 3), (3, 2)]  # cabeza primero
        direction = (0, 1)  # derecha
        food = None
        score = 0
        game_over = False

        def place_food():
            """Coloca comida en una posición aleatoria vacía."""
            occupied = set(snake_body)
            posibles = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in occupied]
            return random.choice(posibles) if posibles else None

        food = place_food()

        def build_board_embed(title_text, desc_text=""):
            """Construye el embed con el tablero."""
            lines = []
            for r in range(ROWS):
                row_chars = []
                for c in range(COLS):
                    if (r, c) == snake_body[0]:
                        row_chars.append("🟢")
                    elif (r, c) in snake_body:
                        row_chars.append("🟩")
                    elif food and (r, c) == food:
                        row_chars.append("🍎")
                    else:
                        row_chars.append("⬛")
                lines.append("".join(row_chars))

            embed = discord.Embed(
                title=title_text,
                description=desc_text + "\n\n" + "\n".join(lines),
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"🐍 {score} puntos")
            return embed

        class SnakeView(discord.ui.View):
            def __init__(self, author):
                super().__init__(timeout=120)
                self.author = author
                self.snake = snake_body[:]
                self.dir = direction
                self.food = food
                self.score = score
                self.over = game_over

            def move(self):
                """Mueve la serpiente en la dirección actual."""
                if self.over:
                    return True

                head_r, head_c = self.snake[0]
                dr, dc = self.dir
                new_head = (head_r + dr, head_c + dc)

                # Verificar colisión con bordes
                if not (0 <= new_head[0] < ROWS and 0 <= new_head[1] < COLS):
                    self.over = True
                    return True

                # Verificar colisión con cuerpo
                if new_head in self.snake[:-1]:
                    self.over = True
                    return True

                # Mover cabeza
                self.snake.insert(0, new_head)

                # Comer comida
                if self.food and new_head == self.food:
                    self.score += 1
                    self.food = place_food()
                    if self.food is None:
                        self.over = True  # ganó, llenó todo
                        return True
                else:
                    self.snake.pop()

                return False

            def can_move(self, new_dir):
                """No puede revertir dirección."""
                dr, dc = new_dir
                hdr, hdc = self.dir
                return (dr * -1, dc * -1) != (hdr, hdc) or len(self.snake) < 2

            async def update_board(self, interaction):
                if self.over:
                    embed = build_board_embed(
                        "💀 GAME OVER",
                        f"Puntuación final: **{self.score}** 🐍"
                    )
                    for child in self.children:
                        child.disabled = True
                    await interaction.response.edit_message(embed=embed, view=self)
                    self.stop()
                    return

                embed = build_board_embed(
                    "🐍 SNAKE",
                    f"Dirección: {'⬆️' if self.dir == (-1,0) else '⬇️' if self.dir == (1,0) else '⬅️' if self.dir == (0,-1) else '➡️'}"
                )
                # Restaurar botones de dirección
                for child in self.children:
                    if isinstance(child, discord.ui.Button):
                        child.disabled = False
                await interaction.response.edit_message(embed=embed, view=self)

            @discord.ui.button(label="⬆️", style=discord.ButtonStyle.secondary, row=0)
            async def up_btn(self, interaction: discord.Interaction, _):
                if interaction.user.id != self.author.id:
                    return await interaction.response.send_message("❌ No es tu juego", ephemeral=True)
                if self.can_move((-1, 0)):
                    self.dir = (-1, 0)
                go = self.move()
                await self.update_board(interaction)

            @discord.ui.button(label="⬇️", style=discord.ButtonStyle.secondary, row=1)
            async def down_btn(self, interaction: discord.Interaction, _):
                if interaction.user.id != self.author.id:
                    return await interaction.response.send_message("❌ No es tu juego", ephemeral=True)
                if self.can_move((1, 0)):
                    self.dir = (1, 0)
                self.move()
                await self.update_board(interaction)

            @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary, row=2)
            async def left_btn(self, interaction: discord.Interaction, _):
                if interaction.user.id != self.author.id:
                    return await interaction.response.send_message("❌ No es tu juego", ephemeral=True)
                if self.can_move((0, -1)):
                    self.dir = (0, -1)
                self.move()
                await self.update_board(interaction)

            @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary, row=2)
            async def right_btn(self, interaction: discord.Interaction, _):
                if interaction.user.id != self.author.id:
                    return await interaction.response.send_message("❌ No es tu juego", ephemeral=True)
                if self.can_move((0, 1)):
                    self.dir = (0, 1)
                self.move()
                await self.update_board(interaction)

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True
                try:
                    embed = build_board_embed(
                        "⏰ TIEMPO AGOTADO",
                        f"Puntuación final: **{self.score}** 🐍"
                    )
                    await self.message.edit(embed=embed, view=self)
                except:
                    pass

        view = SnakeView(ctx.author)
        embed = build_board_embed(
            "🐍 SNAKE",
            "¡Usa los botones para mover la serpiente!\nAtrapa 🍎 para sumar puntos."
        )
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Games(bot))

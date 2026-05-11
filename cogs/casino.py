"""
Casino Cog — Sistema completo de juegos de azar para Mint Bot.

Comandos:
  /slots         — Tragamonedas con 8 símbolos y tabla de pagos.
  /coinflip      — Cara o cruz, doble o nada.
  /dice          — Apuesta a un número (1-6), over (>3) o under (<4).
  /blackjack     — Blackjack contra la casa con botones interactivos.
  /casino-stats  — Estadísticas personales de casino.

Dependencias:
  - Economy cog (para saldos en data/balances.json).
  - data/casino_stats.json (se crea automáticamente).
"""

from __future__ import annotations

import json
import os
import random
from typing import Any, Optional

import discord
from discord.ext import commands

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────

MIN_BET = 10

# Símbolos de la tragamonedas con sus multiplicadores (3 iguales)
SLOT_SYMBOLS: list[dict[str, Any]] = [
    {"emoji": "🍒", "mult": 3, "name": "Cereza"},
    {"emoji": "🍋", "mult": 5, "name": "Limón"},
    {"emoji": "🍊", "mult": 7, "name": "Naranja"},
    {"emoji": "🍇", "mult": 10, "name": "Uva"},
    {"emoji": "🍉", "mult": 12, "name": "Sandía"},
    {"emoji": "⭐",  "mult": 15, "name": "Estrella"},
    {"emoji": "💎", "mult": 20, "name": "Diamante"},
    {"emoji": "7️⃣", "mult": 50, "name": "Siete"},
]

# Mapeo rápido emoji → multiplier
EMOJI_MULT: dict[str, int] = {s["emoji"]: s["mult"] for s in SLOT_SYMBOLS}
EMOJI_LIST: list[str] = [s["emoji"] for s in SLOT_SYMBOLS]

# Colores para embeds
COLOR_GOLD = discord.Color.gold()
COLOR_GREEN = discord.Color.green()
COLOR_RED = discord.Color.red()
COLOR_BLUE = discord.Color.blue()
COLOR_PURPLE = discord.Color.purple()
COLOR_CASINO = discord.Color.from_rgb(0, 153, 51)  # verde casino


# ──────────────────────────────────────────────
# COG PRINCIPAL
# ──────────────────────────────────────────────

class Casino(commands.Cog):
    """🎰 Juegos de casino con monedas reales del bot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.stats_file = "data/casino_stats.json"
        self._load_stats()

    # ------------------------------------------------------------------
    # PERSISTENCIA — Estadísticas de casino
    # ------------------------------------------------------------------

    def _load_stats(self) -> None:
        """Cargar estadísticas de casino desde el archivo JSON."""
        if not os.path.exists("data"):
            os.makedirs("data")
        if os.path.exists(self.stats_file):
            with open(self.stats_file, encoding="utf-8") as f:
                self.stats: dict[str, Any] = json.load(f)
        else:
            self.stats = {}

    def _save_stats(self) -> None:
        """Guardar estadísticas de casino al archivo JSON."""
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # ECONOMÍA — Interacción con Economy cog
    # ------------------------------------------------------------------

    def _get_economy_cog(self) -> Optional[commands.Cog]:
        """Obtener el cog de Economy si está cargado."""
        return self.bot.get_cog("Economy")

    def get_balance(self, user_id: int) -> int:
        """Obtener saldo del usuario desde el Economy cog."""
        economy = self._get_economy_cog()
        if economy is not None:
            return economy.get_balance(user_id)
        # Fallback: lectura directa del archivo de balances
        balance_file = "data/balances.json"
        if os.path.exists(balance_file):
            with open(balance_file, encoding="utf-8") as f:
                balances: dict[str, int] = json.load(f)
            return balances.get(str(user_id), 0)
        return 0

    def add_money(self, user_id: int, amount: int) -> None:
        """Añadir o restar monedas al usuario vía el Economy cog."""
        economy = self._get_economy_cog()
        if economy is not None:
            economy.add_money(user_id, amount)
        else:
            # Fallback: escritura directa
            balance_file = "data/balances.json"
            if not os.path.exists("data"):
                os.makedirs("data")
            balances: dict[str, int] = {}
            if os.path.exists(balance_file):
                with open(balance_file, encoding="utf-8") as f:
                    balances = json.load(f)
            balances[str(user_id)] = balances.get(str(user_id), 0) + amount
            with open(balance_file, "w", encoding="utf-8") as f:
                json.dump(balances, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # ESTADÍSTICAS
    # ------------------------------------------------------------------

    def _update_stats(self, user_id: int, won: bool, amount: int) -> None:
        """Actualizar las estadísticas de casino de un usuario.

        Args:
            user_id: ID de Discord del usuario.
            won: True si ganó, False si perdió.
            amount: Cantidad apostada (siempre positiva).
        """
        uid = str(user_id)
        if uid not in self.stats:
            self.stats[uid] = {
                "wins": 0,
                "losses": 0,
                "net": 0,
                "total_bet": 0,
                "games_played": 0,
            }
        s = self.stats[uid]
        s["games_played"] += 1
        s["total_bet"] += amount
        if won:
            s["wins"] += 1
            s["net"] += amount
        else:
            s["losses"] += 1
            s["net"] -= amount
        self._save_stats()

    def _get_stats(self, user_id: int) -> dict[str, Any]:
        """Obtener estadísticas de un usuario (con valores por defecto)."""
        uid = str(user_id)
        if uid not in self.stats:
            return {
                "wins": 0,
                "losses": 0,
                "net": 0,
                "total_bet": 0,
                "games_played": 0,
            }
        return self.stats[uid]

    # ------------------------------------------------------------------
    # VALIDACIÓN DE APUESTAS
    # ------------------------------------------------------------------

    async def _validate_bet(
        self, ctx: commands.Context, amount: int
    ) -> Optional[int]:
        """Validar una apuesta y devolver el saldo actual, o None si es inválida.

        Envía un mensaje de error efímero si la apuesta no es válida.
        """
        if amount < MIN_BET:
            await ctx.send(
                f"❌ La apuesta mínima es **{MIN_BET}** monedas.",
                ephemeral=True,
            )
            return None

        balance = self.get_balance(ctx.author.id)
        if amount > balance:
            await ctx.send(
                f"❌ No tienes suficientes monedas. Tu saldo es **{balance}**.",
                ephemeral=True,
            )
            return None

        return balance

    # ==================================================================
    # COMANDO: /slots
    # ==================================================================

    @commands.hybrid_command(
        name="slots",
        description="🎰 Juega a la tragamonedas. ¡Alinea 3 símbolos iguales!",
    )
    async def slots(self, ctx: commands.Context, bet: int) -> None:
        """🎰 Tragamonedas — Apuesta y gira 3 rodillos.

        Parámetros
        ----------
        bet : int
            Cantidad de monedas a apostar (mín. 10).
        """
        await ctx.defer()

        balance = await self._validate_bet(ctx, bet)
        if balance is None:
            return

        # Girar los rodillos
        result = [random.choice(EMOJI_LIST) for _ in range(3)]
        a, b, c = result

        # Determinar resultado
        if a == b == c:
            # Tres iguales → gana
            multiplier = EMOJI_MULT[a]
            winnings = bet * multiplier
            prize = winnings - bet  # ganancia neta (lo que realmente añadimos)
            self.add_money(ctx.author.id, prize)
            self._update_stats(ctx.author.id, True, bet)

            embed = discord.Embed(
                title="🎰 ¡TRAGAMONEDAS!",
                description=(
                    f"{' ┃ '.join(result)}\n\n"
                    f"**¡TRES {a} IGUALES!**\n"
                    f"Multiplicador: **×{multiplier}**\n"
                    f"Ganaste **{winnings}** monedas 🎉"
                ),
                color=COLOR_GOLD,
            )
            embed.set_footer(
                text=f"Saldo actual: {self.get_balance(ctx.author.id)} 🪙"
            )
            await ctx.send(embed=embed)

        elif a == b or b == c or a == c:
            # Par → recuperas la apuesta (empuje)
            self._update_stats(ctx.author.id, True, bet)

            embed = discord.Embed(
                title="🎰 TRAGAMONEDAS",
                description=(
                    f"{' ┃ '.join(result)}\n\n"
                    f"**¡Un par!** Recuperas tu apuesta de **{bet}** monedas.\n"
                    "¡Casi fue jackpot! Intenta de nuevo."
                ),
                color=COLOR_BLUE,
            )
            embed.set_footer(
                text=f"Saldo actual: {self.get_balance(ctx.author.id)} 🪙"
            )
            await ctx.send(embed=embed)

        else:
            # Sin coincidencias → pierde
            self.add_money(ctx.author.id, -bet)
            self._update_stats(ctx.author.id, False, bet)

            embed = discord.Embed(
                title="🎰 TRAGAMONEDAS",
                description=(
                    f"{' ┃ '.join(result)}\n\n"
                    f"😢 **Sin suerte...** Perdiste **{bet}** monedas."
                ),
                color=COLOR_RED,
            )
            embed.set_footer(
                text=f"Saldo actual: {self.get_balance(ctx.author.id)} 🪙"
            )
            await ctx.send(embed=embed)

    # ==================================================================
    # COMANDO: /coinflip
    # ==================================================================

    @commands.hybrid_command(
        name="coinflip",
        description="🪙 Cara o cruz — ¡doble o nada!",
    )
    async def coinflip(
        self, ctx: commands.Context, bet: int, choice: str
    ) -> None:
        """🪙 Cara o cruz — Elige cara o cruz. Si aciertas, doblas.

        Parámetros
        ----------
        bet : int
            Cantidad a apostar (mín. 10).
        choice : str
            "cara" o "cruz" (o "heads"/"tails").
        """
        await ctx.defer()

        balance = await self._validate_bet(ctx, bet)
        if balance is None:
            return

        # Normalizar elección
        choice_lower = choice.lower().strip()
        if choice_lower in ("cara", "heads", "c"):
            user_choice = "cara"
        elif choice_lower in ("cruz", "tails", "x"):
            user_choice = "cruz"
        else:
            await ctx.send(
                '❌ Elige **cara** o **cruz** (o **heads**/**tails**).',
                ephemeral=True,
            )
            return

        # Lanzar moneda
        flip = random.choice(["cara", "cruz"])
        won = flip == user_choice

        if won:
            self.add_money(ctx.author.id, bet)
            self._update_stats(ctx.author.id, True, bet)

            embed = discord.Embed(
                title="🪙 ¡CARA O CRUZ!",
                description=(
                    f"La moneda cayó en **{flip}** ✨\n"
                    f"Elegiste **{user_choice}**\n\n"
                    f"🎉 **¡Ganaste!** +**{bet}** monedas.\n"
                    f"Nuevo saldo: **{self.get_balance(ctx.author.id)}** 🪙"
                ),
                color=COLOR_GREEN,
            )
            await ctx.send(embed=embed)
        else:
            self.add_money(ctx.author.id, -bet)
            self._update_stats(ctx.author.id, False, bet)

            embed = discord.Embed(
                title="🪙 CARA O CRUZ",
                description=(
                    f"La moneda cayó en **{flip}** 😔\n"
                    f"Elegiste **{user_choice}**\n\n"
                    f"😢 **Perdiste** **{bet}** monedas.\n"
                    f"Saldo restante: **{self.get_balance(ctx.author.id)}** 🪙"
                ),
                color=COLOR_RED,
            )
            await ctx.send(embed=embed)

    # ==================================================================
    # COMANDO: /dice
    # ==================================================================

    @commands.hybrid_command(
        name="dice",
        description="🎲 Apuesta a un número, over (>3) o under (<4).",
    )
    async def dice(
        self, ctx: commands.Context, bet: int, prediction: str
    ) -> None:
        """🎲 Dado — Predice el resultado del dado (1-6).

        Puedes apostar a:
          • Un número específico (1-6) → paga ×5
          • **over**  (mayor a 3)      → paga ×2
          • **under** (menor a 4)      → paga ×2

        Parámetros
        ----------
        bet : int
            Cantidad a apostar (mín. 10).
        prediction : str
            Número (1-6), "over" o "under".
        """
        await ctx.defer()

        balance = await self._validate_bet(ctx, bet)
        if balance is None:
            return

        pred_lower = prediction.lower().strip()
        roll = random.randint(1, 6)

        # Determinar tipo de apuesta y si ganó
        won = False
        multiplier = 0
        bet_type = ""

        if pred_lower in ("over", "mayor", "alto", ">"):
            bet_type = "over (>3)"
            if roll > 3:
                won = True
                multiplier = 2
        elif pred_lower in ("under", "menor", "bajo", "<"):
            bet_type = "under (<4)"
            if roll < 4:
                won = True
                multiplier = 2
        elif pred_lower.isdigit():
            num = int(pred_lower)
            if 1 <= num <= 6:
                bet_type = f"número {num}"
                if roll == num:
                    won = True
                    multiplier = 5
            else:
                await ctx.send(
                    "❌ El número debe estar entre **1** y **6**.",
                    ephemeral=True,
                )
                return
        else:
            await ctx.send(
                '❌ Apuesta inválida. Usa un número (1-6), **over** o **under**.',
                ephemeral=True,
            )
            return

        # Mostrar el dado con emoji según el resultado
        dice_emojis = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣"}
        dice_display = dice_emojis[roll]

        if won:
            winnings = bet * multiplier
            prize = winnings - bet  # ganancia neta
            self.add_money(ctx.author.id, prize)
            self._update_stats(ctx.author.id, True, bet)

            desc = (
                f"🎲 El dado muestra **{roll}** {dice_display}\n"
                f"Tu apuesta: **{bet_type}**\n\n"
                f"🎉 **¡Ganaste!** ×{multiplier} → +**{winnings}** monedas.\n"
                f"Nuevo saldo: **{self.get_balance(ctx.author.id)}** 🪙"
            )
            embed = discord.Embed(
                title="🎲 ¡DADO!",
                description=desc,
                color=COLOR_GREEN,
            )
            await ctx.send(embed=embed)
        else:
            self.add_money(ctx.author.id, -bet)
            self._update_stats(ctx.author.id, False, bet)

            desc = (
                f"🎲 El dado muestra **{roll}** {dice_display}\n"
                f"Tu apuesta: **{bet_type}**\n\n"
                f"😢 **Perdiste** **{bet}** monedas.\n"
                f"Saldo restante: **{self.get_balance(ctx.author.id)}** 🪙"
            )
            embed = discord.Embed(
                title="🎲 DADO",
                description=desc,
                color=COLOR_RED,
            )
            await ctx.send(embed=embed)

    # ==================================================================
    # COMANDO: /blackjack
    # ==================================================================

    @commands.hybrid_command(
        name="blackjack",
        description="🃏 Blackjack contra la casa. ¡Llega a 21 sin pasarte!",
    )
    async def blackjack(self, ctx: commands.Context, bet: int) -> None:
        """🃏 Blackjack — Juega al blackjack contra el bot.

        Parámetros
        ----------
        bet : int
            Cantidad a apostar (mín. 10).
        """
        balance = await self._validate_bet(ctx, bet)
        if balance is None:
            return

        # Iniciar partida
        game = BlackjackGame(ctx.author, bet, self)
        await game.start(ctx)

    # ==================================================================
    # COMANDO: /casino-stats
    # ==================================================================

    @commands.hybrid_command(
        name="casino-stats",
        description="📊 Tus estadísticas de casino (ganadas, perdidas, neto).",
    )
    async def casino_stats(self, ctx: commands.Context) -> None:
        """📊 Estadísticas — Muestra tus estadísticas de casino."""
        await ctx.defer()

        stats = self._get_stats(ctx.author.id)
        total = stats["games_played"]
        wins = stats["wins"]
        losses = stats["losses"]
        net = stats["net"]
        total_bet = stats["total_bet"]

        winrate = (wins / total * 100) if total > 0 else 0

        # Determinar color según ganancias
        if net > 0:
            color = COLOR_GREEN
            trend = "📈"
        elif net < 0:
            color = COLOR_RED
            trend = "📉"
        else:
            color = COLOR_BLUE
            trend = "📊"

        embed = discord.Embed(
            title=f"{trend} Estadísticas de Casino",
            description=f"Resumen de **{ctx.author.display_name}**",
            color=color,
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        embed.add_field(name="🎮 Partidas jugadas", value=f"**{total}**", inline=True)
        embed.add_field(name="✅ Ganadas", value=f"**{wins}**", inline=True)
        embed.add_field(name="❌ Perdidas", value=f"**{losses}**", inline=True)
        embed.add_field(name="📊 Winrate", value=f"**{winrate:.1f}%**", inline=True)
        embed.add_field(name="💰 Total apostado", value=f"**{total_bet}** 🪙", inline=True)
        embed.add_field(name="💵 Ganancia neta", value=f"**{net:+d}** 🪙", inline=True)

        if total > 0:
            embed.set_footer(text="¡Sigue jugando para mejorar tus estadísticas!")

        await ctx.send(embed=embed)


# ──────────────────────────────────────────────
# BLACKJACK — Lógica y Vista Interactiva
# ──────────────────────────────────────────────

class BlackjackGame:
    """Maneja una partida de blackjack con botones interactivos."""

    SUITS = ["♠", "♥", "♦", "♣"]
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(
        self, player: discord.Member, bet: int, cog: Casino
    ) -> None:
        self.player = player
        self.bet = bet
        self.cog = cog

        self.deck: list[tuple[str, str]] = []
        self.player_hand: list[tuple[str, str]] = []
        self.dealer_hand: list[tuple[str, str]] = []
        self.game_over = False
        self.message: Optional[discord.Message] = None
        self._build_deck()

    # ── Mazo ──────────────────────────────────

    def _build_deck(self) -> None:
        """Crear y barajar un mazo de 52 cartas."""
        self.deck = [(rank, suit) for suit in self.SUITS for rank in self.RANKS]
        random.shuffle(self.deck)

    def _draw(self) -> tuple[str, str]:
        """Robar una carta del mazo."""
        return self.deck.pop()

    # ── Puntuación ────────────────────────────

    @staticmethod
    def _hand_value(hand: list[tuple[str, str]]) -> int:
        """Calcular el valor de una mano de blackjack."""
        value = 0
        aces = 0
        for rank, _ in hand:
            if rank in ("J", "Q", "K"):
                value += 10
            elif rank == "A":
                aces += 1
                value += 11
            else:
                value += int(rank)
        # Convertir Ases de 11→1 si nos pasamos
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value

    # ── Visualización ─────────────────────────

    @staticmethod
    def _card_display(rank: str, suit: str) -> str:
        """Representación de una carta como texto."""
        return f"**{rank}{suit}**"

    @staticmethod
    def _hand_display(hand: list[tuple[str, str]]) -> str:
        """Mostrar una mano completa."""
        return " ".join(
            BlackjackGame._card_display(r, s) for r, s in hand
        )

    @staticmethod
    def _hand_value_str(hand: list[tuple[str, str]]) -> str:
        """Mostrar el valor de la mano."""
        return f"**{BlackjackGame._hand_value(hand)}**"

    def _build_embed(self, reveal_dealer: bool = False) -> discord.Embed:
        """Construir el embed con el estado actual de la partida."""
        player_val = self._hand_value(self.player_hand)
        dealer_val = self._hand_value(self.dealer_hand)

        desc = (
            f"**Apuesta:** {self.bet} 🪙\n\n"
            f"**Tu mano:** {self._hand_display(self.player_hand)}\n"
            f"Valor: {self._hand_value_str(self.player_hand)}\n\n"
        )

        if reveal_dealer or self.game_over:
            desc += (
                f"**Mano de la casa:** {self._hand_display(self.dealer_hand)}\n"
                f"Valor: {self._hand_value_str(self.dealer_hand)}\n"
            )
        else:
            # Mostrar solo la primera carta
            first_card = self._card_display(*self.dealer_hand[0])
            desc += (
                f"**Mano de la casa:** {first_card} 🂠\n"
                f"Valor: **{self._hand_value([self.dealer_hand[0]])}** + ?\n"
            )

        # Determinar color y título según estado
        if self.game_over:
            if player_val > 21:
                color = COLOR_RED
                title = "🃏 ¡Te pasaste! 😵"
            elif dealer_val > 21:
                color = COLOR_GREEN
                title = "🃏 ¡La casa se pasó! 🎉"
            elif player_val > dealer_val:
                color = COLOR_GREEN
                title = "🃏 ¡Ganaste! 🎉"
            elif player_val == dealer_val:
                color = COLOR_BLUE
                title = "🃏 Empuje (Push) 🤝"
            else:
                color = COLOR_RED
                title = "🃏 Perdiste 😢"
        else:
            color = COLOR_CASINO
            title = "🃏 Blackjack"

        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_author(
            name=self.player.display_name,
            icon_url=self.player.display_avatar.url,
        )

        if not self.game_over:
            embed.set_footer(text="Presiona un botón para jugar.")

        return embed

    # ── Flujo de la partida ───────────────────

    async def start(self, ctx: commands.Context) -> None:
        """Iniciar la partida: repartir cartas y enviar el mensaje con botones.

        Args:
            ctx: Contexto del comando (usado para enviar el mensaje inicial).
        """
        # Repartir dos cartas a cada uno
        self.player_hand = [self._draw(), self._draw()]
        self.dealer_hand = [self._draw(), self._draw()]

        player_val = self._hand_value(self.player_hand)

        # Verificar blackjack inmediato
        if player_val == 21:
            await self._resolve(ctx)
            return

        # Enviar embed con botones
        view = BlackjackView(self)
        embed = self._build_embed()
        self.message = await ctx.send(embed=embed, view=view)

    async def _resolve(
        self, ctx: commands.Context, interaction: Optional[discord.Interaction] = None
    ) -> None:
        """Resolver la partida: la casa juega, se determina el ganador y se muestra el resultado.

        Args:
            ctx: Contexto del comando (usado si no hay mensaje previo).
            interaction: Interacción opcional (si se llama desde un botón).
        """
        self.game_over = True

        player_val = self._hand_value(self.player_hand)
        dealer_val = self._hand_value(self.dealer_hand)

        # La casa juega automáticamente si el jugador no se pasó
        if player_val <= 21:
            while dealer_val < 17:
                self.dealer_hand.append(self._draw())
                dealer_val = self._hand_value(self.dealer_hand)

        # Determinar ganador y ajustar saldo
        if player_val > 21:
            # Jugador se pasó → pierde
            self.cog.add_money(self.player.id, -self.bet)
            self.cog._update_stats(self.player.id, False, self.bet)
        elif dealer_val > 21:
            # Casa se pasó → jugador gana (2:1)
            self.cog.add_money(self.player.id, self.bet)
            self.cog._update_stats(self.player.id, True, self.bet)
        elif player_val > dealer_val:
            # Jugador gana (2:1)
            self.cog.add_money(self.player.id, self.bet)
            self.cog._update_stats(self.player.id, True, self.bet)
        elif player_val == dealer_val:
            # Empuje (push) → se devuelve la apuesta, no hay cambio neto
            self.cog._update_stats(self.player.id, True, self.bet)
        else:
            # Casa gana
            self.cog.add_money(self.player.id, -self.bet)
            self.cog._update_stats(self.player.id, False, self.bet)

        embed = self._build_embed(reveal_dealer=True)
        embed.set_footer(
            text=f"Saldo actual: {self.cog.get_balance(self.player.id)} 🪙"
        )

        # Si hay interacción, responder a través de ella; si no, editar mensaje o enviar nuevo
        if interaction is not None:
            await interaction.response.edit_message(embed=embed, view=None)
        elif self.message is not None:
            await self.message.edit(embed=embed, view=None)
        else:
            await ctx.send(embed=embed)

    async def hit(self, interaction: discord.Interaction) -> None:
        """Pedir otra carta (botón)."""
        if interaction.user.id != self.player.id:
            await interaction.response.send_message(
                "❌ No es tu partida.", ephemeral=True
            )
            return

        self.player_hand.append(self._draw())
        player_val = self._hand_value(self.player_hand)

        if player_val > 21:
            # Se pasó, fin del juego
            await self._resolve(None, interaction)
        elif player_val == 21:
            # Llegó a 21, se planta automáticamente
            await self.stand(interaction)
        else:
            embed = self._build_embed()
            await interaction.response.edit_message(
                embed=embed, view=BlackjackView(self)
            )

    async def stand(self, interaction: discord.Interaction) -> None:
        """Plantarse y dejar que juegue la casa (botón)."""
        if interaction.user.id != self.player.id:
            await interaction.response.send_message(
                "❌ No es tu partida.", ephemeral=True
            )
            return

        await self._resolve(None, interaction)


class BlackjackView(discord.ui.View):
    """Botones interactivos de Hit y Stand para Blackjack."""

    def __init__(self, game: BlackjackGame) -> None:
        super().__init__(timeout=60)
        self.game = game

    @discord.ui.button(
        label="Pedir carta", style=discord.ButtonStyle.green, emoji="🃏"
    )
    async def hit_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.game.hit(interaction)

    @discord.ui.button(
        label="Plantarse", style=discord.ButtonStyle.red, emoji="✋"
    )
    async def stand_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await self.game.stand(interaction)

    async def on_timeout(self) -> None:
        """Cuando el tiempo se acaba, se deshabilitan los botones."""
        if self.game.message is None:
            return
        if self.game.game_over:
            return

        # Marcar como game_over y resolver automáticamente (stand forzado)
        self.game.game_over = True

        player_val = BlackjackGame._hand_value(self.game.player_hand)
        dealer_val = BlackjackGame._hand_value(self.game.dealer_hand)

        # La casa juega
        if player_val <= 21:
            while dealer_val < 17:
                self.game.dealer_hand.append(self.game._draw())
                dealer_val = BlackjackGame._hand_value(self.game.dealer_hand)

        # Determinar ganador (misma lógica que _resolve)
        if player_val > 21:
            self.game.cog.add_money(self.game.player.id, -self.game.bet)
            self.game.cog._update_stats(self.game.player.id, False, self.game.bet)
        elif dealer_val > 21:
            self.game.cog.add_money(self.game.player.id, self.game.bet)
            self.game.cog._update_stats(self.game.player.id, True, self.game.bet)
        elif player_val > dealer_val:
            self.game.cog.add_money(self.game.player.id, self.game.bet)
            self.game.cog._update_stats(self.game.player.id, True, self.game.bet)
        elif player_val == dealer_val:
            self.game.cog._update_stats(self.game.player.id, True, self.game.bet)
        else:
            self.game.cog.add_money(self.game.player.id, -self.game.bet)
            self.game.cog._update_stats(self.game.player.id, False, self.game.bet)

        embed = self.game._build_embed(reveal_dealer=True)
        embed.set_footer(
            text=f"⏰ Tiempo agotado • "
                 f"Saldo actual: {self.game.cog.get_balance(self.game.player.id)} 🪙"
        )

        try:
            await self.game.message.edit(embed=embed, view=None)
        except discord.errors.NotFound:
            pass  # El mensaje pudo haber sido eliminado


# ──────────────────────────────────────────────
# SETUP
# ──────────────────────────────────────────────

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Casino(bot))

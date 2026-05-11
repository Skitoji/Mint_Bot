"""
Trading Cog — Mercado de acciones y cryptos para Mint Bot.

Comandos:
  /stocks      — Muestra el mercado disponible
  /buy         — Compra acciones de una empresa/crypto
  /sell        — Vende tus acciones
  /portfolio   — Muestra tu cartera de inversiones
  /stonks      — Precios en vivo (simulados)
  /price       — Precio actual de un activo

Dependencias:
  - Economy cog (para saldos)
  - data/trading.json (se crea automáticamente)
"""

from __future__ import annotations

import json
import os
import random
from typing import Any, Optional

import discord
from discord import app_commands
from discord.ext import commands

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────

COLOR_GREEN = discord.Color.green()
COLOR_RED = discord.Color.red()
COLOR_GOLD = discord.Color.gold()
COLOR_BLUE = discord.Color.blue()
COLOR_PURPLE = discord.Color.purple()
COLOR_ORANGE = discord.Color.orange()

ASSETS: list[dict[str, Any]] = [
    # Acciones
    {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock", "base_price": 178.0},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "stock", "base_price": 141.0},
    {"symbol": "MSFT", "name": "Microsoft Corp.", "type": "stock", "base_price": 378.0},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "type": "stock", "base_price": 178.0},
    {"symbol": "NVDA", "name": "NVIDIA Corp.", "type": "stock", "base_price": 875.0},
    {"symbol": "TSLA", "name": "Tesla Inc.", "type": "stock", "base_price": 248.0},
    {"symbol": "META", "name": "Meta Platforms Inc.", "type": "stock", "base_price": 505.0},
    {"symbol": "NFLX", "name": "Netflix Inc.", "type": "stock", "base_price": 605.0},
    {"symbol": "DIS", "name": "The Walt Disney Co.", "type": "stock", "base_price": 112.0},
    {"symbol": "KO", "name": "The Coca-Cola Co.", "type": "stock", "base_price": 61.0},
    # Cryptos
    {"symbol": "BTC", "name": "Bitcoin", "type": "crypto", "base_price": 67000.0},
    {"symbol": "ETH", "name": "Ethereum", "type": "crypto", "base_price": 3450.0},
    {"symbol": "SOL", "name": "Solana", "type": "crypto", "base_price": 172.0},
    {"symbol": "XRP", "name": "Ripple", "type": "crypto", "base_price": 0.62},
    {"symbol": "ADA", "name": "Cardano", "type": "crypto", "base_price": 0.47},
    {"symbol": "DOGE", "name": "Dogecoin", "type": "crypto", "base_price": 0.15},
    {"symbol": "DOT", "name": "Polkadot", "type": "crypto", "base_price": 7.50},
    {"symbol": "AVAX", "name": "Avalanche", "type": "crypto", "base_price": 38.0},
]

TRADING_FILE = "data/trading.json"
MIN_BUY = 1
PRICE_VOLATILITY = 0.05  # 5% max fluctuation per call


# ──────────────────────────────────────────────
# COG
# ──────────────────────────────────────────────

class Trading(commands.Cog):
    """📊 Compra y venta de acciones y cryptos."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._ensure_data_dir()
        self._load_portfolios()

    # ─── Persistencia ──────────────────────────────────────────────────

    def _ensure_data_dir(self) -> None:
        if not os.path.exists("data"):
            os.makedirs("data")

    def _load_portfolios(self) -> None:
        if os.path.exists(TRADING_FILE):
            with open(TRADING_FILE, encoding="utf-8") as f:
                self.portfolios: dict[str, dict[str, float]] = json.load(f)
        else:
            self.portfolios = {}
            self._save_portfolios()

    def _save_portfolios(self) -> None:
        with open(TRADING_FILE, "w", encoding="utf-8") as f:
            json.dump(self.portfolios, f, indent=2, ensure_ascii=False)

    # ─── Precios simulados ────────────────────────────────────────────

    def _get_price(self, asset: dict[str, Any]) -> float:
        """Simula el precio actual con fluctuación aleatoria."""
        fluctuation = asset["base_price"] * PRICE_VOLATILITY
        return round(asset["base_price"] + random.uniform(-fluctuation, fluctuation), 2)

    def _get_all_prices(self) -> dict[str, float]:
        """Obtiene precios actuales de todos los activos."""
        return {a["symbol"]: self._get_price(a) for a in ASSETS}

    # ─── Cartera ──────────────────────────────────────────────────────

    def _get_portfolio(self, user_id: int) -> dict[str, float]:
        """Obtiene la cartera de un usuario."""
        uid = str(user_id)
        if uid not in self.portfolios:
            self.portfolios[uid] = {}
        return self.portfolios[uid]

    def _get_economy(self):
        return self.bot.get_cog("Economy")

    # ─── Comandos ─────────────────────────────────────────────────────

    @commands.hybrid_command(
        name="stocks",
        description="📊 Muestra el mercado disponible de acciones y cryptos",
    )
    async def stocks(self, ctx: commands.Context) -> None:
        """Muestra todos los activos disponibles en el mercado con precios actuales."""
        await ctx.defer()

        prices = self._get_all_prices()

        embed = discord.Embed(
            title="📊 MERCADO FINANCIERO",
            description="Cotizaciones actuales (simuladas con fluctuación ±5%)",
            color=COLOR_GOLD,
        )

        stocks_list = []
        cryptos_list = []
        for asset in ASSETS:
            symbol = asset["symbol"]
            price = prices[symbol]
            emoji = "📈" if random.random() > 0.5 else "📉"
            line = f"{emoji} **{symbol}** — ${price:,.2f}  *({asset['name']})*"
            if asset["type"] == "stock":
                stocks_list.append(line)
            else:
                cryptos_list.append(line)

        embed.add_field(
            name="🏢 Acciones",
            value="\n".join(stocks_list) if stocks_list else "Sin datos",
            inline=False,
        )
        embed.add_field(
            name="🪙 Cryptos",
            value="\n".join(cryptos_list) if cryptos_list else "Sin datos",
            inline=False,
        )
        embed.set_footer(text="Usa /buy <símbolo> <cantidad> para comprar")

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="buy",
        description="💰 Compra acciones de una empresa o crypto",
    )
    @app_commands.describe(
        simbolo="Símbolo del activo (ej: AAPL, BTC)",
        cantidad="Cantidad de acciones a comprar",
    )
    async def buy(
        self, ctx: commands.Context, simbolo: str, cantidad: int = 1
    ) -> None:
        """Compra acciones de un activo del mercado.

        Parámetros
        ----------
        simbolo : str
            Símbolo del activo (AAPL, BTC, ETH, etc.).
        cantidad : int
            Número de acciones a comprar (mín. 1).
        """
        await ctx.defer()

        economy = self._get_economy()
        if economy is None:
            await ctx.send("❌ El sistema económico no está disponible.")
            return

        simbolo = simbolo.upper()
        asset = next((a for a in ASSETS if a["symbol"] == simbolo), None)
        if asset is None:
            await ctx.send(
                f"❌ Activo **{simbolo}** no encontrado. Usa `/stocks` para ver el mercado."
            )
            return

        if cantidad < MIN_BUY:
            await ctx.send(f"❌ Debes comprar al menos **{MIN_BUY}** unidad.")
            return

        price = self._get_price(asset)
        total_cost = round(price * cantidad, 2)

        # Convertir a coins (1 coin = $1, redondeado)
        cost_coins = max(1, round(total_cost))

        balance = economy.get_balance(ctx.author.id)
        if cost_coins > balance:
            await ctx.send(
                f"❌ No tienes suficientes monedas.\n"
                f"**{cantidad}** × **{simbolo}** = **{cost_coins}** 🪙\n"
                f"Tu saldo: **{balance}** 🪙"
            )
            return

        # Descontar coins
        economy.add_money(ctx.author.id, -cost_coins)

        # Agregar a cartera
        portfolio = self._get_portfolio(ctx.author.id)
        portfolio[simbolo] = portfolio.get(simbolo, 0) + cantidad
        self._save_portfolios()

        embed = discord.Embed(
            title="✅ COMPRA REALIZADA",
            description=(
                f"Compraste **{cantidad}** × **{simbolo}** ({asset['name']})\n"
                f"Precio unitario: **${price:,.2f}**\n"
                f"Total pagado: **{cost_coins}** 🪙\n\n"
                f"Nuevo saldo: **{economy.get_balance(ctx.author.id)}** 🪙"
            ),
            color=COLOR_GREEN,
        )
        embed.set_footer(text=f"Tienes {portfolio.get(simbolo, 0)} {simbolo} en cartera")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="sell",
        description="💸 Vende tus acciones de una empresa o crypto",
    )
    @app_commands.describe(
        simbolo="Símbolo del activo a vender",
        cantidad="Cantidad de acciones a vender (opcional, por defecto todas)",
    )
    async def sell(
        self, ctx: commands.Context, simbolo: str, cantidad: Optional[int] = None
    ) -> None:
        """Vende acciones de tu cartera.

        Parámetros
        ----------
        simbolo : str
            Símbolo del activo a vender.
        cantidad : int, optional
            Cantidad a vender. Si se omite, vende todas.
        """
        await ctx.defer()

        economy = self._get_economy()
        if economy is None:
            await ctx.send("❌ El sistema económico no está disponible.")
            return

        simbolo = simbolo.upper()
        portfolio = self._get_portfolio(ctx.author.id)

        if simbolo not in portfolio or portfolio[simbolo] <= 0:
            await ctx.send(
                f"❌ No tienes **{simbolo}** en tu cartera. Usa `/portfolio` para ver tus activos."
            )
            return

        owned = portfolio[simbolo]
        if cantidad is None or cantidad > owned:
            cantidad = owned

        asset = next((a for a in ASSETS if a["symbol"] == simbolo), None)
        if asset is None:
            await ctx.send("❌ Activo no reconocido.")
            return

        price = self._get_price(asset)
        total_value = round(price * cantidad, 2)
        value_coins = max(1, round(total_value))

        # Vender
        portfolio[simbolo] -= cantidad
        if portfolio[simbolo] <= 0:
            del portfolio[simbolo]
        self._save_portfolios()

        # Añadir coins
        economy.add_money(ctx.author.id, value_coins)

        embed = discord.Embed(
            title="✅ VENTA REALIZADA",
            description=(
                f"Vendiste **{cantidad}** × **{simbolo}** ({asset['name']})\n"
                f"Precio unitario: **${price:,.2f}**\n"
                f"Total recibido: **{value_coins}** 🪙\n\n"
                f"Nuevo saldo: **{economy.get_balance(ctx.author.id)}** 🪙"
            ),
            color=COLOR_ORANGE,
        )

        remaining = portfolio.get(simbolo, 0)
        if remaining > 0:
            embed.set_footer(text=f"Te quedan {remaining} {simbolo} en cartera")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="portfolio",
        description="📁 Muestra tu cartera de inversiones",
    )
    async def portfolio(self, ctx: commands.Context) -> None:
        """Muestra todos tus activos y su valor actual."""
        await ctx.defer()

        portfolio = self._get_portfolio(ctx.author.id)

        if not portfolio:
            await ctx.send(
                "📁 **Tu cartera está vacía.**\nUsa `/buy <símbolo> <cantidad>` para invertir."
            )
            return

        prices = self._get_all_prices()
        total_value = 0

        embed = discord.Embed(
            title=f"📁 CARTERA DE {ctx.author.display_name}",
            color=COLOR_BLUE,
        )

        lines = []
        for symbol, amount in sorted(portfolio.items()):
            if amount <= 0:
                continue
            price = prices.get(symbol, 0)
            asset_value = round(price * amount, 2)
            total_value += asset_value

            asset = next((a for a in ASSETS if a["symbol"] == symbol), None)
            name = asset["name"] if asset else symbol
            emoji = "🏢" if (asset and asset["type"] == "stock") else "🪙"

            lines.append(
                f"{emoji} **{symbol}** × {amount}\n"
                f"└ ${price:,.2f} c/u → **${asset_value:,.2f}**"
            )

        embed.description = "\n".join(lines)
        embed.add_field(
            name="💰 Valor total de cartera",
            value=f"**${total_value:,.2f}** ≈ **{max(1, round(total_value))}** 🪙",
            inline=False,
        )
        embed.set_footer(text="Usa /sell <símbolo> para vender")

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="stonks",
        description="📈 Precios en vivo del mercado (simulados)",
    )
    async def stonks(self, ctx: commands.Context) -> None:
        """Muestra los precios actualizados de todos los activos."""
        await ctx.defer()

        prices = self._get_all_prices()

        embed = discord.Embed(
            title="📈 PRECIOS EN VIVO",
            description="Fluctuación simulada ±5% en cada consulta",
            color=COLOR_GREEN,
        )

        for asset in ASSETS:
            price = prices[asset["symbol"]]
            emoji = "📈" if random.random() > 0.5 else "📉"
            embed.add_field(
                name=f"{emoji} {asset['symbol']}",
                value=f"${price:,.2f}\n*{asset['name']}*",
                inline=True,
            )

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="price",
        description="🔍 Precio actual de un activo específico",
    )
    @app_commands.describe(simbolo="Símbolo del activo (ej: AAPL, BTC)")
    async def price(self, ctx: commands.Context, simbolo: str) -> None:
        """Muestra el precio actual de un activo."""
        await ctx.defer()

        simbolo = simbolo.upper()
        asset = next((a for a in ASSETS if a["symbol"] == simbolo), None)

        if asset is None:
            await ctx.send(
                f"❌ Activo **{simbolo}** no encontrado. Usa `/stocks` para ver el mercado."
            )
            return

        price = self._get_price(asset)
        emoji = "📈" if random.random() > 0.5 else "📉"

        embed = discord.Embed(
            title=f"{emoji} {simbolo} — {asset['name']}",
            description=f"Precio actual: **${price:,.2f}**\nTipo: **{asset['type'].upper()}**",
            color=COLOR_PURPLE,
        )
        await ctx.send(embed=embed)


# ──────────────────────────────────────────────
# SETUP
# ──────────────────────────────────────────────

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Trading(bot))

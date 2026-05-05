import discord
from discord.ext import commands
import json
import os
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balance_file = "data/balances.json"
        self.load_balances()
    
    def load_balances(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if os.path.exists(self.balance_file):
            with open(self.balance_file) as f:
                self.balances = json.load(f)
        else:
            self.balances = {}
    
    def save_balances(self):
        with open(self.balance_file, "w") as f:
            json.dump(self.balances, f, indent=2)
    
    def get_balance(self, user_id):
        return self.balances.get(str(user_id), 0)
    
    def add_money(self, user_id, amount):
        user_id = str(user_id)
        self.balances[user_id] = self.balances.get(user_id, 0) + amount
        self.save_balances()
    
    @commands.hybrid_command(name="work", description="Trabaja y gana monedas")
    async def work(self, ctx):
        await ctx.defer()
        earnings = random.randint(50, 150)
        self.add_money(ctx.author.id, earnings)
        await ctx.send(f"💼 {ctx.author.mention} trabajaste y ganaste **{earnings}** monedas.")
    
    @commands.hybrid_command(name="daily", description="Recompensa diaria")
    async def daily(self, ctx):
        await ctx.defer()
        # Aquí podrías añadir lógica de cooldown (opcional)
        reward = 200
        self.add_money(ctx.author.id, reward)
        await ctx.send(f"📅 {ctx.author.mention} reclamaste tu recompensa diaria: **{reward}** monedas.")
    
    @commands.hybrid_command(name="gamble", description="Apuesta monedas (50% de ganar)")
    async def gamble(self, ctx, amount: int):
        await ctx.defer()
        if amount <= 0:
            await ctx.send("❌ Apuesta una cantidad positiva.", ephemeral=True)
            return
        balance = self.get_balance(ctx.author.id)
        if amount > balance:
            await ctx.send(f"❌ No tienes suficientes monedas. Tienes {balance}.", ephemeral=True)
            return
        if random.choice([True, False]):
            self.add_money(ctx.author.id, amount)
            await ctx.send(f"🎉 ¡Ganaste! +{amount} monedas. Nuevo saldo: {self.get_balance(ctx.author.id)}")
        else:
            self.add_money(ctx.author.id, -amount)
            await ctx.send(f"😢 Perdiste {amount} monedas. Saldo restante: {self.get_balance(ctx.author.id)}")
    
    @commands.hybrid_command(name="slots", description="Juego de tragamonedas")
    async def slots(self, ctx, bet: int):
        await ctx.defer()
        balance = self.get_balance(ctx.author.id)
        if bet <= 0 or bet > balance:
            await ctx.send(f"❌ Apuesta inválida. Tienes {balance} monedas.", ephemeral=True)
            return
        emojis = ["🍒", "🍋", "🍊", "7️⃣"]
        result = [random.choice(emojis) for _ in range(3)]
        if result[0] == result[1] == result[2]:
            multiplier = 5 if result[0] == "7️⃣" else 3
            win = bet * multiplier
            self.add_money(ctx.author.id, win)
            await ctx.send(f"🎰 | {' '.join(result)} | ¡JACKPOT! Ganaste {win} monedas.")
        else:
            self.add_money(ctx.author.id, -bet)
            await ctx.send(f"🎰 | {' '.join(result)} | Perdiste {bet} monedas.")
    
    @commands.hybrid_command(name="top", description="Ranking de monedas")
    async def top(self, ctx, tipo: str = "coins"):
        await ctx.defer()
        if tipo.lower() != "coins":
            await ctx.send("❌ Por ahora solo disponible `top coins`.", ephemeral=True)
            return
        sorted_balances = sorted(self.balances.items(), key=lambda x: x[1], reverse=True)[:10]
        if not sorted_balances:
            await ctx.send("No hay datos aún.")
            return
        embed = discord.Embed(title="💰 Ranking de monedas", color=discord.Color.gold())
        for idx, (uid, bal) in enumerate(sorted_balances, 1):
            user = self.bot.get_user(int(uid)) or await self.bot.fetch_user(int(uid))
            name = user.display_name if user else uid
            embed.add_field(name=f"{idx}. {name}", value=f"{bal} monedas", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
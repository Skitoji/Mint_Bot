import discord
from discord.ext import commands
import json
import os
import random
import time
from datetime import datetime, timezone, timedelta

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balance_file = "data/balances.json"
        self.work_daily_file = "data/work_daily.json"
        self.daily_cooldown_file = "data/daily_cooldown.json"
        self.work_cooldown = {}  # {user_id: last_use_timestamp}
        
        self.load_balances()
        self.load_work_daily()
        self.load_daily_cooldown()
    
    # ========== BALANCES ==========
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
    
    # ========== WORK DAILY LIMIT ==========
    def load_work_daily(self):
        if os.path.exists(self.work_daily_file):
            with open(self.work_daily_file) as f:
                self.work_daily = json.load(f)
        else:
            self.work_daily = {}
    
    def save_work_daily(self):
        with open(self.work_daily_file, "w") as f:
            json.dump(self.work_daily, f, indent=2)
    
    def get_today_str(self):
        # Usamos UTC para consistencia
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def can_work(self, user_id):
        user_id = str(user_id)
        today = self.get_today_str()
        data = self.work_daily.get(user_id, {})
        last_date = data.get("date", "")
        count = data.get("count", 0)
        
        if last_date != today:
            # Nuevo día, reiniciar contador
            return True, 25, 0
        else:
            remaining = 25 - count
            if remaining > 0:
                return True, remaining, count
            else:
                return False, 0, count
    
    def register_work(self, user_id):
        user_id = str(user_id)
        today = self.get_today_str()
        if user_id not in self.work_daily:
            self.work_daily[user_id] = {"date": today, "count": 1}
        else:
            if self.work_daily[user_id]["date"] != today:
                self.work_daily[user_id] = {"date": today, "count": 1}
            else:
                self.work_daily[user_id]["count"] += 1
        self.save_work_daily()
    
    # ========== DAILY COOLDOWN ==========
    def load_daily_cooldown(self):
        if os.path.exists(self.daily_cooldown_file):
            with open(self.daily_cooldown_file) as f:
                self.daily_cooldown = json.load(f)
        else:
            self.daily_cooldown = {}
    
    def save_daily_cooldown(self):
        with open(self.daily_cooldown_file, "w") as f:
            json.dump(self.daily_cooldown, f, indent=2)
    
    def can_claim_daily(self, user_id):
        user_id = str(user_id)
        last_claim = self.daily_cooldown.get(user_id, 0)
        now = time.time()
        if now - last_claim >= 86400:  # 24 horas
            return True, 0
        else:
            remaining = int(86400 - (now - last_claim))
            return False, remaining
    
    def register_daily(self, user_id):
        self.daily_cooldown[str(user_id)] = time.time()
        self.save_daily_cooldown()
    
    # ========== COMANDOS ==========
    @commands.hybrid_command(name="work", description="Trabaja y gana monedas (límite 25 veces al día)")
    async def work(self, ctx):
        await ctx.defer()
        user_id = ctx.author.id
        
        # Cooldown de 3 segundos entre usos (evita spam)
        now = time.time()
        last = self.work_cooldown.get(user_id, 0)
        if now - last < 3:
            await ctx.send(f"⏳ Espera {3 - int(now - last)} segundos antes de volver a trabajar.", ephemeral=True)
            return
        self.work_cooldown[user_id] = now
        
        # Verificar límite diario
        can, remaining, used = self.can_work(user_id)
        if not can:
            await ctx.send(f"❌ Ya usaste tus **25 trabajos** de hoy. Vuelve mañana.", ephemeral=True)
            return
        
        earnings = random.randint(50, 200)
        self.add_money(user_id, earnings)
        self.register_work(user_id)
        
        await ctx.send(f"💼 {ctx.author.mention} trabajaste y ganaste **{earnings}** monedas. (Te quedan {remaining-1} trabajos hoy)")
    
    @commands.hybrid_command(name="daily", description="Recompensa diaria (solo una vez cada 24h)")
    async def daily(self, ctx):
        await ctx.defer()
        user_id = ctx.author.id
        
        can, remaining_seconds = self.can_claim_daily(user_id)
        if not can:
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            await ctx.send(f"❌ Ya reclamaste tu recompensa diaria. Vuelve en **{hours}h {minutes}m**.", ephemeral=True)
            return
        
        reward = 500
        self.add_money(user_id, reward)
        self.register_daily(user_id)
        await ctx.send(f"📅 {ctx.author.mention} reclamaste tu recompensa diaria: **{reward}** monedas. Vuelve mañana.")
    
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
    
    # ========== COMANDO SECRETO DE ADMIN ==========
    @commands.command(name="addcoins")
    async def addcoins(self, ctx, user: discord.Member, amount: int):
        """Comando secreto para añadir coins (solo owner)"""
        OWNER_ID = 756527487474860223
        if ctx.author.id != OWNER_ID:
            return  # No responde nada, como si no existiera
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser positiva.", ephemeral=True)
            return
        self.add_money(user.id, amount)
        await ctx.send(f"✅ Se añadieron **{amount}** coins a {user.mention}. Nuevo saldo: {self.get_balance(user.id)}")

async def setup(bot):
    await bot.add_cog(Economy(bot))
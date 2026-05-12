import discord
from discord.ext import commands
from discord import app_commands
import json, os, random, asyncio
from datetime import datetime, timedelta
from utils.ui import error_embed, success_embed, info_embed
from utils.colors import COLORS

DATA_FILE = "data/economy.json"

def load_economy():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_economy(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user_data(user_id):
    data = load_economy()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "money": 100,
            "bank": 0,
            "bank_max": 1000,
            "gems": 0,
            "daily_streak": 0,
            "last_daily": "",
            "total_earned": 0,
            "total_lost": 0
        }
    return data, data[uid]

def save_user_data(user_id, user_data):
    data = load_economy()
    data[str(user_id)] = user_data
    save_economy(data)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._lock = asyncio.Lock()
        self.rob_cooldown = commands.CooldownMapping.from_cooldown(1, 3600, commands.BucketType.user)
        self.work_cooldown = commands.CooldownMapping.from_cooldown(1, 3600, commands.BucketType.user)

    @commands.hybrid_command(name="balance", aliases=["bal", "money"], description="Revisa tu saldo actual")
    async def balance(self, ctx, miembro: discord.Member = None):
        objetivo = miembro or ctx.author
        data, user_data = get_user_data(objetivo.id)
        total = user_data["money"] + user_data["bank"]
        embed = discord.Embed(
            title=f"💰 Saldo de {objetivo.display_name}",
            color=discord.Color.gold()
        )
        embed.add_field(name="🪙 Efectivo", value=f"**{user_data['money']:,}** monedas", inline=True)
        embed.add_field(name="🏦 Banco", value=f"**{user_data['bank']:,}** / {user_data['bank_max']:,}", inline=True)
        embed.add_field(name="💎 Gemas", value=f"**{user_data['gems']:,}**", inline=True)
        embed.set_footer(text=f"Patrimonio total: {total:,} monedas")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="deposit", aliases=["dep"], description="Deposita dinero al banco (seguro)")
    @app_commands.describe(cantidad="Cantidad a depositar o 'all' para depositar todo")
    async def deposit(self, ctx, cantidad: str):
        async with self._lock:
            _, user_data = get_user_data(ctx.author.id)
            if cantidad.lower() == "all" or cantidad.lower() == "todo":
                depositar = user_data["money"]
            else:
                try:
                    depositar = int(cantidad.replace(",", ""))
                except ValueError:
                    await ctx.send(embed=error_embed("❌ Cantidad inválida"), ephemeral=True)
                    return
            if depositar <= 0:
                await ctx.send(embed=error_embed("❌ Ingresa una cantidad positiva"), ephemeral=True)
                return
            if depositar > user_data["money"]:
                await ctx.send(embed=error_embed("❌ No tienes suficiente efectivo"), ephemeral=True)
                return
            espacio = user_data["bank_max"] - user_data["bank"]
            if depositar > espacio:
                depositar = espacio
                if depositar == 0:
                    await ctx.send(embed=error_embed("❌ Tu banco está lleno. Usa `/upgrade-bank` para ampliarlo"), ephemeral=True)
                    return
            user_data["money"] -= depositar
            user_data["bank"] += depositar
            save_user_data(ctx.author.id, user_data)
        await ctx.send(embed=success_embed(f"✅ Depositaste **{depositar:,}** monedas en el banco"))

    @commands.hybrid_command(name="withdraw", aliases=["with"], description="Retira dinero del banco")
    @app_commands.describe(cantidad="Cantidad a retirar o 'all' para retirar todo")
    async def withdraw(self, ctx, cantidad: str):
        async with self._lock:
            _, user_data = get_user_data(ctx.author.id)
            if cantidad.lower() == "all" or cantidad.lower() == "todo":
                retirar = user_data["bank"]
            else:
                try:
                    retirar = int(cantidad.replace(",", ""))
                except ValueError:
                    await ctx.send(embed=error_embed("❌ Cantidad inválida"), ephemeral=True)
                    return
            if retirar <= 0:
                await ctx.send(embed=error_embed("❌ Ingresa una cantidad positiva"), ephemeral=True)
                return
            if retirar > user_data["bank"]:
                await ctx.send(embed=error_embed("❌ No tienes tanto en el banco"), ephemeral=True)
                return
            user_data["bank"] -= retirar
            user_data["money"] += retirar
            save_user_data(ctx.author.id, user_data)
        await ctx.send(embed=success_embed(f"✅ Retiraste **{retirar:,}** monedas del banco"))

    @commands.hybrid_command(name="bank", description="Ver información del banco")
    async def bank(self, ctx):
        _, user_data = get_user_data(ctx.author.id)
        embed = discord.Embed(title="🏦 Tu Banco", color=discord.Color.blue())
        embed.add_field(name="Depositado", value=f"**{user_data['bank']:,}** monedas", inline=True)
        embed.add_field(name="Capacidad", value=f"**{user_data['bank_max']:,}** monedas", inline=True)
        embed.add_field(name="Disponible", value=f"**{user_data['bank_max'] - user_data['bank']:,}** espacios", inline=True)
        embed.set_footer(text="Usa /deposit y /withdraw para gestionar tu banco")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="upgrade-bank", aliases=["upbank"], description="Amplía la capacidad de tu banco")
    @app_commands.describe(cantidad="Nueva capacidad a añadir (ej: 1000)")
    async def upgrade_bank(self, ctx, cantidad: int):
        if cantidad <= 0:
            await ctx.send(embed=error_embed("❌ La cantidad debe ser positiva"), ephemeral=True)
            return
        costo = cantidad * 2
        async with self._lock:
            _, user_data = get_user_data(ctx.author.id)
            if user_data["money"] < costo:
                await ctx.send(embed=error_embed(f"❌ Necesitas **{costo:,}** monedas para ampliar **{cantidad:,}** espacios (costo: 2x)"), ephemeral=True)
                return
            user_data["money"] -= costo
            user_data["bank_max"] += cantidad
            save_user_data(ctx.author.id, user_data)
        await ctx.send(embed=success_embed(f"✅ Banco ampliado! Ahora tienes **{user_data['bank_max']:,}** de capacidad máxima"))

    @commands.hybrid_command(name="daily", description="Reclama tu recompensa diaria")
    async def daily(self, ctx):
        async with self._lock:
            _, user_data = get_user_data(ctx.author.id)
            hoy = datetime.now().strftime("%Y-%m-%d")
            if user_data["last_daily"] == hoy:
                await ctx.send(embed=error_embed("❌ Ya reclamaste tu daily hoy. Vuelve mañana!"), ephemeral=True)
                return
            ayer = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if user_data["last_daily"] == ayer:
                user_data["daily_streak"] += 1
            else:
                user_data["daily_streak"] = 1
            streak = user_data["daily_streak"]
            bonus = min(streak * 50, 1000)
            base = 100
            total = base + bonus
            user_data["money"] += total
            user_data["last_daily"] = hoy
            user_data["total_earned"] = user_data.get("total_earned", 0) + total
            save_user_data(ctx.author.id, user_data)
        embed = discord.Embed(title="🎁 Recompensa Diaria", color=discord.Color.green())
        embed.add_field(name="Base", value=f"**{base:,}**", inline=True)
        embed.add_field(name="Racha", value=f"**{streak}** día(s) (+{bonus:,})", inline=True)
        embed.add_field(name="Total", value=f"**+{total:,}** monedas!", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="weekly", description="Reclama tu recompensa semanal")
    async def weekly(self, ctx):
        async with self._lock:
            _, user_data = get_user_data(ctx.author.id)
            hoy = datetime.now()
            semana_actual = hoy.isocalendar()[1]
            if user_data.get("last_weekly_week") == semana_actual:
                await ctx.send(embed=error_embed("❌ Ya reclamaste tu recompensa semanal!"), ephemeral=True)
                return
            user_data["money"] += 500
            user_data["gems"] = user_data.get("gems", 0) + 5
            user_data["last_weekly_week"] = semana_actual
            user_data["total_earned"] = user_data.get("total_earned", 0) + 500
            save_user_data(ctx.author.id, user_data)
        await ctx.send(embed=success_embed("🎉 Recompensa semanal: **+500** monedas y **+5** gemas!"))

    @commands.hybrid_command(name="work", description="Trabaja para ganar dinero")
    async def work(self, ctx):
        bucket = self.work_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            segundos = int(retry_after)
            await ctx.send(embed=error_embed(f"⏳ Descansa un poco! Vuelve en **{segundos//60}** minutos"), ephemeral=True)
            return
        ganancia = random.randint(50, 200)
        trabajos = [
            "programaste una app", "cocinaste en un restaurante", "diste clases de matemáticas",
            "reparaste computadoras", "diseñaste un logo", "tradujiste documentos",
            "limpiaste jardines", "cuidaste mascotas", "vendiste arte digital",
            "hiciste entregas en bici", "tocaste música en la calle", "fotografiaste un evento"
        ]
        trabajo = random.choice(trabajos)
        async with self._lock:
            _, user_data = get_user_data(ctx.author.id)
            user_data["money"] += ganancia
            user_data["total_earned"] = user_data.get("total_earned", 0) + ganancia
            save_user_data(ctx.author.id, user_data)
        embed = discord.Embed(title="💼 Trabajo", description=f"Has {trabajo} y ganaste **{ganancia:,}** monedas!", color=discord.Color.green())
        embed.set_footer(text="Próximo trabajo disponible en 1 hora")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="beg", description="Pide limosna")
    async def beg(self, ctx):
        resultados = [
            ("un desconocido te dio", random.randint(1, 20)),
            ("tu abuela te envió", random.randint(10, 50)),
            ("encontraste en el suelo", random.randint(1, 10)),
            ("alguien muy generoso te dio", random.randint(20, 100)),
            ("un perro callejero te trajo", random.randint(1, 5)),
            ("una IA muy generosa te donó", random.randint(50, 200)),
        ]
        if random.random() < 0.15:
            await ctx.send(embed=error_embed("😔 Nadie te dio nada hoy. Sigue intentando!"))
            return
        accion, ganancia = random.choice(resultados)
        if random.random() < 0.1:
            ganancia *= 2
            accion += " (¡propina doble!)"
        async with self._lock:
            _, user_data = get_user_data(ctx.author.id)
            user_data["money"] += ganancia
            user_data["total_earned"] = user_data.get("total_earned", 0) + ganancia
            save_user_data(ctx.author.id, user_data)
        await ctx.send(embed=success_embed(f"🙏 {accion} **{ganancia:,}** monedas!"))

    @commands.hybrid_command(name="rob", aliases=["steal"], description="Intenta robar a otro usuario")
    @app_commands.describe(objetivo="Usuario al que quieres robar")
    async def rob(self, ctx, objetivo: discord.Member):
        if objetivo.id == ctx.author.id:
            await ctx.send(embed=error_embed("❌ No puedes robarte a ti mismo"), ephemeral=True)
            return
        if objetivo.bot:
            await ctx.send(embed=error_embed("❌ No puedes robar a un bot"), ephemeral=True)
            return
        bucket = self.rob_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            segundos = int(retry_after)
            await ctx.send(embed=error_embed(f"🕵️‍♂️ La policía te busca aún! Espera **{segundos//60}** min"), ephemeral=True)
            return
        async with self._lock:
            _, ladron_data = get_user_data(ctx.author.id)
            _, victima_data = get_user_data(objetivo.id)
            if victima_data["money"] < 50:
                await ctx.send(embed=error_embed(f"😅 {objetivo.display_name} ni siquiera tiene 50 monedas sueltas... pobre"), ephemeral=True)
                return
            exito = random.random() < 0.3
            if exito:
                max_robo = min(int(victima_data["money"] * 0.2), 5000)
                robado = random.randint(50, max_robo)
                victima_data["money"] -= robado
                ladron_data["money"] += robado
                victima_data["total_lost"] = victima_data.get("total_lost", 0) + robado
                save_user_data(ctx.author.id, ladron_data)
                save_user_data(objetivo.id, victima_data)
                await ctx.send(embed=success_embed(f"🦹 Robaste **{robado:,}** monedas a {objetivo.display_name}!"))
            else:
                multa = min(int(ladron_data["money"] * 0.5), int(victima_data["money"] * 0.3))
                if multa > 0:
                    ladron_data["money"] -= multa
                    victima_data["money"] += multa
                    save_user_data(ctx.author.id, ladron_data)
                    save_user_data(objetivo.id, victima_data)
                await ctx.send(embed=error_embed(f"🚔 Te atraparon! Pagaste **{multa:,}** monedas a {objetivo.display_name}"))

    @commands.hybrid_command(name="give", aliases=["pay"], description="Regala dinero a otro usuario")
    @app_commands.describe(objetivo="Usuario que recibirá el dinero", cantidad="Cantidad a regalar")
    async def give(self, ctx, objetivo: discord.Member, cantidad: int):
        if cantidad <= 0:
            await ctx.send(embed=error_embed("❌ Cantidad inválida"), ephemeral=True)
            return
        if objetivo.id == ctx.author.id:
            await ctx.send(embed=error_embed("❌ No puedes darte dinero a ti mismo"), ephemeral=True)
            return
        async with self._lock:
            _, donante_data = get_user_data(ctx.author.id)
            _, receptor_data = get_user_data(objetivo.id)
            if donante_data["money"] < cantidad:
                await ctx.send(embed=error_embed("❌ No tienes suficiente dinero"), ephemeral=True)
                return
            donante_data["money"] -= cantidad
            receptor_data["money"] += cantidad
            save_user_data(ctx.author.id, donante_data)
            save_user_data(objetivo.id, receptor_data)
        await ctx.send(embed=success_embed(f"🎁 Le diste **{cantidad:,}** monedas a {objetivo.display_name}!"))

    @commands.hybrid_command(name="leaderboard", aliases=["lb", "top"], description="Top de los más ricos del servidor")
    async def leaderboard(self, ctx):
        data = load_economy()
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("money", 0) + x[1].get("bank", 0), reverse=True)
        embed = discord.Embed(title="🏆 Top Riqueza", color=discord.Color.gold())
        desc = ""
        medallas = ["🥇", "🥈", "🥉"]
        for i, (uid, info) in enumerate(sorted_users[:10]):
            total = info.get("money", 0) + info.get("bank", 0)
            try:
                user = await self.bot.fetch_user(int(uid))
                nombre = user.display_name if user else f"Usuario {uid}"
            except:
                nombre = f"Usuario {uid}"
            medalla = medallas[i] if i < 3 else f"**{i+1}.**"
            desc += f"{medalla} {nombre} — **{total:,}** 💰\n"
        embed.description = desc
        await ctx.send(embed=embed)

    # ─── INTERFACE FOR OTHER COGS ───
    def get_balance(self, user_id: int) -> int:
        """Obtener saldo de un usuario (usado por Casino cog)."""
        _, user_data = get_user_data(user_id)
        return user_data["money"]

    def add_money(self, user_id: int, amount: int) -> bool:
        """Añade o resta dinero de un usuario (usado por Casino cog)."""
        import json, os
        data = load_economy()
        uid = str(user_id)
        if uid in data:
            data[uid]["money"] = data[uid].get("money", 0) + amount
            data[uid]["total_earned"] = data[uid].get("total_earned", 0) + max(0, amount)
            data[uid]["total_lost"] = data[uid].get("total_lost", 0) + max(0, -amount)
            save_economy(data)
            return True
        return False

    @commands.hybrid_command(name="rob-stats", aliases=["theftstats"], description="Estadísticas de robos")
    async def rob_stats(self, ctx):
        _, user_data = get_user_data(ctx.author.id)
        embed = discord.Embed(title="📊 Tus Estadísticas", color=discord.Color.blurple())
        embed.add_field(name="💰 Total Ganado", value=f"**{user_data.get('total_earned', 0):,}** monedas")
        embed.add_field(name="💸 Total Perdido", value=f"**{user_data.get('total_lost', 0):,}** monedas")
        neto = user_data.get('total_earned', 0) - user_data.get('total_lost', 0)
        embed.add_field(name="📈 Neto", value=f"**{neto:,}** monedas")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="gamble", description="Apuesta coins (50% ganar, 50% perder)")
    @app_commands.describe(cantidad="Cantidad de coins a apostar")
    async def gamble(self, ctx, cantidad: int):
        """Apuesta tus coins — &gamble <cantidad>"""
        if cantidad <= 0:
            await ctx.send(embed=error_embed("❌ La cantidad debe ser mayor a 0"), ephemeral=True)
            return

        _, user_data = get_user_data(ctx.author.id)
        if user_data["money"] < cantidad:
            await ctx.send(embed=error_embed("❌ No tienes suficiente dinero"), ephemeral=True)
            return

        resultado = random.choice(["ganaste", "perdiste"])
        if resultado == "ganaste":
            user_data["money"] += cantidad
            embed = success_embed(f"🎉 ¡Ganaste **{cantidad:,}** coins! Ahora tienes **{user_data['money']:,}** coins")
        else:
            user_data["money"] -= cantidad
            embed = error_embed(f"😢 Perdiste **{cantidad:,}** coins. Te quedan **{user_data['money']:,}** coins")

        data = load_economy()
        data[str(ctx.author.id)] = user_data
        save_economy(data)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="pagar", description="Transfiere coins a otro usuario")
    @app_commands.describe(usuario="Usuario a quien pagar", cantidad="Cantidad de coins")
    async def pagar(self, ctx, usuario: discord.Member, cantidad: int):
        """Paga a otro usuario — &pagar @usuario <cantidad>"""
        # Reutilizar la lógica de /give
        donante_data = get_user_data(ctx.author.id)[1]
        receptor_data = get_user_data(usuario.id)[1]

        if cantidad <= 0:
            await ctx.send(embed=error_embed("❌ La cantidad debe ser mayor a 0"), ephemeral=True)
            return
        if usuario.id == ctx.author.id:
            await ctx.send(embed=error_embed("❌ No puedes pagarte a ti mismo"), ephemeral=True)
            return
        if donante_data["money"] < cantidad:
            await ctx.send(embed=error_embed("❌ No tienes suficiente dinero"), ephemeral=True)
            return

        donante_data["money"] -= cantidad
        receptor_data["money"] += cantidad

        data = load_economy()
        data[str(ctx.author.id)] = donante_data
        data[str(usuario.id)] = receptor_data
        save_economy(data)

        await ctx.send(embed=success_embed(f"💸 Le pagaste **{cantidad:,}** coins a {usuario.display_name}!"))

async def setup(bot):
    await bot.add_cog(Economy(bot))

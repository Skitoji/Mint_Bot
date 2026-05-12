from discord.ext import commands, tasks
import json, os, random, asyncio
import discord
from utils import ui

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "data/xp.json"
        self._lock = asyncio.Lock()
        self.load_data()
        self.auto_save.start()

    def cog_unload(self):
        self.auto_save.cancel()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file) as f:
                self.xp_data = json.load(f)
        else:
            self.xp_data = {}

    async def save_data(self):
        async with self._lock:
            with open(self.data_file, "w") as f:
                json.dump(self.xp_data, f, indent=2)

    @tasks.loop(seconds=60.0)
    async def auto_save(self):
        await self.save_data()

    def xp_to_next(self, level):
        return 100 + (level - 1) * 50

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        if user_id not in self.xp_data:
            self.xp_data[user_id] = {"xp": 0, "level": 1}

        gain = random.randint(8, 15)
        self.xp_data[user_id]["xp"] += gain

        nxt = self.xp_to_next(self.xp_data[user_id]["level"])
        if self.xp_data[user_id]["xp"] >= nxt:
            self.xp_data[user_id]["xp"] -= nxt
            self.xp_data[user_id]["level"] += 1
            try:
                await message.channel.send(f"🎉 {message.author.mention} subió al nivel **{self.xp_data[user_id]['level']}**!")
            except:
                pass

    # @commands.command()
    # async def perfil(self, ctx, user=None):
    #     """(Deprecado) Ver perfil usando el comando /profile"""
    #     pass

    # ──────────────────────────────────────────────
    #  Comandos de XP
    # ──────────────────────────────────────────────

    @commands.hybrid_command(name="level", aliases=["nivel"], description="Muestra tu nivel de XP o el de otro usuario")
    @app_commands.describe(usuario="Usuario del que quieres ver el nivel (opcional)")
    async def level(self, ctx: commands.Context, usuario: discord.User = None):
        """Ver nivel de XP — &level @usuario"""
        usuario = usuario or ctx.author
        user_id = str(usuario.id)

        if user_id not in self.xp_data:
            await ctx.send(embed=ui.simple_embed(
                "⭐ Sin XP",
                f"{usuario.mention} todavía no tiene XP.",
                color=discord.Color.purple()
            ))
            return

        data = self.xp_data[user_id]
        lvl = data["level"]
        xp = data["xp"]
        next_xp = self.xp_to_next(lvl)
        progress = xp / next_xp * 100 if next_xp > 0 else 0

        bar = "▓" * int(progress // 10) + "░" * (10 - int(progress // 10))

        embed = ui.simple_embed(
            f"⭐ Nivel de {usuario.display_name}",
            f"**Nivel:** {lvl}\n"
            f"**XP:** {xp}/{next_xp}\n"
            f"**Progreso:** `{bar}` {progress:.0f}%",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rank", aliases=["posicion", "ranking"], description="Muestra tu puesto en el ranking de XP")
    @app_commands.describe(usuario="Usuario del que quieres ver el ranking (opcional)")
    async def rank(self, ctx: commands.Context, usuario: discord.User = None):
        """Ver puesto en ranking XP — &rank @usuario"""
        usuario = usuario or ctx.author
        user_id = str(usuario.id)

        if user_id not in self.xp_data:
            await ctx.send(embed=ui.simple_embed(
                "📊 Sin datos",
                f"{usuario.mention} no aparece en el ranking (aún sin XP).",
                color=discord.Color.purple()
            ))
            return

        # Ordenar todos los usuarios por nivel y XP
        sorted_users = sorted(
            self.xp_data.items(),
            key=lambda x: (x[1].get("level", 0), x[1].get("xp", 0)),
            reverse=True
        )

        # Encontrar la posición del usuario
        position = next((i+1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id), None)

        if position is None:
            await ctx.send(embed=ui.info_embed("📊 Ranking", f"{usuario.mention} no está en el ranking."))
            return

        total = len(sorted_users)
        medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"#{position}"
        data = self.xp_data[user_id]

        embed = ui.simple_embed(
            f"📊 Ranking de {usuario.display_name}",
            f"**Posición:** {medal} de {total}\n"
            f"**Nivel:** {data['level']}\n"
            f"**XP:** {data['xp']}",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    if bot.get_cog("XP") is not None:
        print("⚠️ Cog 'XP' ya cargado - omitiendo carga duplicada")
        return
    await bot.add_cog(XP(bot))

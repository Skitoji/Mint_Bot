from discord.ext import commands, tasks
import json, os, random, asyncio

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

async def setup(bot):
    if bot.get_cog("XP") is not None:
        print("⚠️ Cog 'XP' ya cargado - omitiendo carga duplicada")
        return
    await bot.add_cog(XP(bot))

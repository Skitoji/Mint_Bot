import discord
from discord.ext import commands
from discord import app_commands
import json, os, asyncio
from datetime import datetime, timedelta
from utils.ui import error_embed, success_embed, info_embed

WARNS_FILE = "data/warns.json"
SNIPE_FILE = "data/snipe.json"
GUILD_CONFIG = "data/guild_config.json"

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default if default else {}

def save_json(path, data):
    os.makedirs("data", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._lock = asyncio.Lock()
        self.snipe_cache = {}

    # ─── COG LISTENERS ───
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        guild_id = str(message.guild.id) if message.guild else "dm"
        if guild_id not in self.snipe_cache:
            self.snipe_cache[guild_id] = []
        self.snipe_cache[guild_id].insert(0, {
            "author_id": message.author.id,
            "author_name": str(message.author),
            "content": message.content or "[embed/sticker]",
            "channel_id": message.channel.id,
            "timestamp": datetime.now().isoformat()
        })
        self.snipe_cache[guild_id] = self.snipe_cache[guild_id][:5]

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        guild_id = str(before.guild.id) if before.guild else "dm"
        if guild_id not in self.snipe_cache:
            self.snipe_cache[guild_id] = []
        self.snipe_cache[guild_id].insert(0, {
            "author_id": before.author.id,
            "author_name": str(before.author),
            "before": before.content or "[embed]",
            "after": after.content or "[embed]",
            "channel_id": before.channel.id,
            "type": "edit",
            "timestamp": datetime.now().isoformat()
        })
        self.snipe_cache[guild_id] = self.snipe_cache[guild_id][:5]

    # ─── WARN SYSTEM ───
    @commands.hybrid_command(name="warn", description="Advierte a un usuario")
    @app_commands.describe(usuario="Usuario a advertir", razon="Motivo de la advertencia")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, usuario: discord.Member, *, razon: str = "No especificada"):
        warns = load_json(WARNS_FILE, {})
        guild_id = str(ctx.guild.id)
        user_id = str(usuario.id)
        if guild_id not in warns:
            warns[guild_id] = {}
        if user_id not in warns[guild_id]:
            warns[guild_id][user_id] = []
        warn_id = len(warns[guild_id][user_id]) + 1
        warns[guild_id][user_id].append({
            "id": warn_id,
            "mod": str(ctx.author),
            "mod_id": ctx.author.id,
            "reason": razon,
            "timestamp": datetime.now().isoformat()
        })
        save_json(WARNS_FILE, warns)
        embed = discord.Embed(title="⚠️ Advertencia", color=discord.Color.orange())
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="Razón", value=razon, inline=False)
        embed.add_field(name="Total", value=f"{len(warns[guild_id][user_id])} advertencia(s)")
        await ctx.send(embed=embed)
        try:
            await usuario.send(embed=error_embed(f"⚠️ Recibiste una advertencia en **{ctx.guild.name}**: {razon}"))
        except:
            pass

    @commands.hybrid_command(name="warnings", aliases=["warns"], description="Ver advertencias de un usuario")
    @app_commands.describe(usuario="Usuario a revisar")
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, usuario: discord.Member):
        warns = load_json(WARNS_FILE, {})
        user_warns = warns.get(str(ctx.guild.id), {}).get(str(usuario.id), [])
        if not user_warns:
            await ctx.send(embed=success_embed(f"✅ {usuario.display_name} no tiene advertencias"))
            return
        embed = discord.Embed(title=f"⚠️ Advertencias de {usuario.display_name}", color=discord.Color.orange())
        for w in user_warns:
            embed.add_field(
                name=f"#{w['id']} — {w['timestamp'][:10]}",
                value=f"Mod: {w['mod']}\nRazón: {w['reason']}",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="clearwarns", aliases=["delwarns"], description="Limpia todas las advertencias de un usuario")
    @app_commands.describe(usuario="Usuario a limpiar advertencias")
    @commands.has_permissions(kick_members=True)
    async def clearwarns(self, ctx, usuario: discord.Member):
        warns = load_json(WARNS_FILE, {})
        guild_id = str(ctx.guild.id)
        if guild_id in warns and str(usuario.id) in warns[guild_id]:
            del warns[guild_id][str(usuario.id)]
            save_json(WARNS_FILE, warns)
        await ctx.send(embed=success_embed(f"✅ Advertencias de {usuario.display_name} eliminadas"))

    @commands.hybrid_command(name="delwarn", description="Elimina una advertencia específica")
    @app_commands.describe(usuario="Usuario", warn_id="ID de la advertencia")
    @commands.has_permissions(kick_members=True)
    async def delwarn(self, ctx, usuario: discord.Member, warn_id: int):
        warns = load_json(WARNS_FILE, {})
        guild_id = str(ctx.guild.id)
        user_warns = warns.get(guild_id, {}).get(str(usuario.id), [])
        filtered = [w for w in user_warns if w["id"] != warn_id]
        if len(filtered) == len(user_warns):
            await ctx.send(embed=error_embed(f"❌ No se encontró la advertencia #{warn_id}"), ephemeral=True)
            return
        warns[guild_id][str(usuario.id)] = filtered
        save_json(WARNS_FILE, warns)
        await ctx.send(embed=success_embed(f"✅ Advertencia #{warn_id} eliminada de {usuario.display_name}"))

    # ─── MODERATION ───
    @commands.hybrid_command(name="kick", description="Expulsa a un usuario del servidor")
    @app_commands.describe(usuario="Usuario a expulsar", razon="Motivo")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, usuario: discord.Member, *, razon: str = "No especificada"):
        if ctx.author.top_role <= usuario.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(embed=error_embed("❌ No puedes expulsar a alguien con un rol igual o superior"), ephemeral=True)
            return
        await usuario.kick(reason=razon)
        await ctx.send(embed=success_embed(f"👢 {usuario.mention} fue expulsado. Razón: {razon}"))

    @commands.hybrid_command(name="ban", description="Banea a un usuario del servidor")
    @app_commands.describe(usuario="Usuario a banear", razon="Motivo", dias="Días de mensajes a eliminar (0-7)")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, usuario: discord.Member, dias: int = 0, *, razon: str = "No especificada"):
        if ctx.author.top_role <= usuario.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(embed=error_embed("❌ No puedes banear a alguien con un rol igual o superior"), ephemeral=True)
            return
        await usuario.ban(reason=razon, delete_message_days=min(dias, 7))
        await ctx.send(embed=success_embed(f"🔨 {usuario.mention} fue baneado. Razón: {razon}"))

    @commands.hybrid_command(name="unban", description="Desbanea a un usuario por ID o nombre")
    @app_commands.describe(usuario="ID o nombre del usuario")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, usuario: str):
        bans = [entry async for entry in ctx.guild.bans()]
        for entry in bans:
            if str(entry.user.id) == usuario or entry.user.name.lower() in usuario.lower():
                await ctx.guild.unban(entry.user)
                await ctx.send(embed=success_embed(f"✅ {entry.user.mention} fue desbaneado"))
                return
        await ctx.send(embed=error_embed("❌ No se encontró al usuario en la lista de baneados"), ephemeral=True)

    @commands.hybrid_command(name="tempban", description="Baneo temporal (automático)")
    @app_commands.describe(usuario="Usuario", duracion="Duración (ej: 1h, 1d, 7d)", razon="Motivo")
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, usuario: discord.Member, duracion: str, *, razon: str = "No especificada"):
        if ctx.author.top_role <= usuario.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(embed=error_embed("❌ No puedes banear a alguien con un rol igual o superior"), ephemeral=True)
            return
        segundos = 0
        if duracion.endswith("h"):
            segundos = int(duracion[:-1]) * 3600
        elif duracion.endswith("d"):
            segundos = int(duracion[:-1]) * 86400
        elif duracion.endswith("m"):
            segundos = int(duracion[:-1]) * 60
        else:
            try:
                segundos = int(duracion)
            except:
                await ctx.send(embed=error_embed("❌ Formato inválido. Usa: 1h, 2d, 30m"), ephemeral=True)
                return
        if segundos < 60 or segundos > 2592000:
            await ctx.send(embed=error_embed("❌ La duración debe ser entre 1 minuto y 30 días"), ephemeral=True)
            return
        await ctx.guild.ban(usuario, reason=razon)
        await ctx.send(embed=success_embed(f"🔨 {usuario.mention} baneado por {duracion}. Razón: {razon}"))
        await asyncio.sleep(segundos)
        try:
            await ctx.guild.unban(usuario, reason="Tempban expirado")
        except:
            pass

    @commands.hybrid_command(name="timeout", aliases=["mute"], description="Silencia a un usuario temporalmente")
    @app_commands.describe(usuario="Usuario", minutos="Duración en minutos (máx 40320)", razon="Motivo")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, usuario: discord.Member, minutos: int = 60, *, razon: str = "No especificada"):
        if ctx.author.top_role <= usuario.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(embed=error_embed("❌ No puedes silenciar a alguien con un rol igual o superior"), ephemeral=True)
            return
        duracion = timedelta(minutes=min(minutos, 40320))
        await usuario.timeout(duracion, reason=razon)
        await ctx.send(embed=success_embed(f"🔇 {usuario.mention} silenciado por {minutos} minutos. Razón: {razon}"))

    @commands.hybrid_command(name="slowmode", description="Establece slowmode en un canal")
    @app_commands.describe(segundos="Segundos entre mensajes (0 para desactivar)", canal="Canal objetivo")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, segundos: int = 5, canal: discord.TextChannel = None):
        canal = canal or ctx.channel
        if segundos < 0 or segundos > 21600:
            await ctx.send(embed=error_embed("❌ El slowmode debe ser entre 0 y 21600 segundos"), ephemeral=True)
            return
        await canal.edit(slowmode_delay=segundos)
        if segundos == 0:
            await ctx.send(embed=success_embed(f"✅ Slowmode desactivado en {canal.mention}"))
        else:
            await ctx.send(embed=success_embed(f"🐢 Slowmode de **{segundos}s** activado en {canal.mention}"))

    @commands.hybrid_command(name="lock", description="Bloquea un canal para @everyone")
    @app_commands.describe(canal="Canal a bloquear")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, canal: discord.TextChannel = None):
        canal = canal or ctx.channel
        await canal.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=success_embed(f"🔒 {canal.mention} bloqueado"))

    @commands.hybrid_command(name="unlock", description="Desbloquea un canal para @everyone")
    @app_commands.describe(canal="Canal a desbloquear")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, canal: discord.TextChannel = None):
        canal = canal or ctx.channel
        await canal.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(embed=success_embed(f"🔓 {canal.mention} desbloqueado"))

    @commands.hybrid_command(name="purge", aliases=["clear", "clean"], description="Elimina mensajes en masa")
    @app_commands.describe(cantidad="Número de mensajes a eliminar (1-100)")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, cantidad: int = 10):
        if cantidad < 1 or cantidad > 100:
            await ctx.send(embed=error_embed("❌ Solo puedes eliminar entre 1 y 100 mensajes"), ephemeral=True)
            return
        await ctx.defer(ephemeral=True)
        deleted = await ctx.channel.purge(limit=min(cantidad, 100))
        await ctx.send(embed=success_embed(f"🧹 Se eliminaron **{len(deleted)}** mensajes"), ephemeral=True, delete_after=5)

    @commands.hybrid_command(name="nuke", description="Clona y elimina un canal (lo regenera)")
    @app_commands.describe(canal="Canal a nukear")
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx, canal: discord.TextChannel = None):
        canal = canal or ctx.channel
        new_channel = await canal.clone(reason="Nuke command")
        await canal.delete(reason="Nuke command")
        await new_channel.send(embed=success_embed("💣 Canal regenerado!"))
        if ctx.channel.id != canal.id:
            await ctx.send(embed=success_embed(f"💣 {canal.mention} ha sido nukeado"))

    # ─── SNIPE ───
    @commands.hybrid_command(name="snipe", description="Muestra el último mensaje eliminado")
    @app_commands.describe(canal="Canal a revisar")
    @commands.has_permissions(read_message_history=True)
    async def snipe(self, ctx, canal: discord.TextChannel = None):
        canal = canal or ctx.channel
        guild_id = str(ctx.guild.id)
        messages = self.snipe_cache.get(guild_id, [])
        # Filter for this channel, only deletions
        channel_msgs = [m for m in messages if m.get("channel_id") == canal.id and "type" not in m]
        if not channel_msgs:
            await ctx.send(embed=error_embed("❌ No hay mensajes eliminados recientes"), ephemeral=True)
            return
        msg = channel_msgs[0]
        try:
            author = await self.bot.fetch_user(msg["author_id"])
            avatar = author.display_avatar.url
        except:
            avatar = None
        embed = discord.Embed(title="👻 Mensaje eliminado", description=msg["content"][:2000], color=discord.Color.blurple())
        embed.set_author(name=msg["author_name"], icon_url=avatar)
        embed.set_footer(text=f"#{canal.name} • {msg['timestamp'][:19]}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="editsnipe", aliases=["esnipe"], description="Muestra el último mensaje editado")
    @app_commands.describe(canal="Canal a revisar")
    @commands.has_permissions(read_message_history=True)
    async def editsnipe(self, ctx, canal: discord.TextChannel = None):
        canal = canal or ctx.channel
        guild_id = str(ctx.guild.id)
        messages = self.snipe_cache.get(guild_id, [])
        channel_msgs = [m for m in messages if m.get("channel_id") == canal.id and m.get("type") == "edit"]
        if not channel_msgs:
            await ctx.send(embed=error_embed("❌ No hay mensajes editados recientes"), ephemeral=True)
            return
        msg = channel_msgs[0]
        embed = discord.Embed(title="📝 Mensaje editado", color=discord.Color.yellow())
        embed.add_field(name="Antes", value=msg["before"][:1024], inline=False)
        embed.add_field(name="Después", value=msg["after"][:1024], inline=False)
        embed.set_author(name=msg["author_name"])
        embed.set_footer(text=f"#{canal.name} • {msg['timestamp'][:19]}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))

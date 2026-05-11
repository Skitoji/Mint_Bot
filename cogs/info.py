import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from typing import Optional


class Info(commands.Cog):
    """Comandos de información del servidor, usuarios y el bot"""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now(timezone.utc)

    # ─── UTILIDADES ─────────────────────────────────────────

    @staticmethod
    def _format_date(dt: datetime) -> str:
        """Formatea una fecha a formato legible en español"""
        if dt is None:
            return "Desconocido"
        return f"<t:{int(dt.timestamp())}:F>"

    @staticmethod
    def _format_date_relative(dt: datetime) -> str:
        """Formato relativo de fecha (ej: hace 2 días)"""
        if dt is None:
            return "Desconocido"
        return f"<t:{int(dt.timestamp())}:R>"

    @property
    def _uptime(self) -> str:
        """Tiempo que lleva el bot encendido en formato legible"""
        now = datetime.now(timezone.utc)
        delta = now - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)

    # ─── COMANDOS ───────────────────────────────────────────

    @commands.hybrid_command(name="userinfo", description="Muestra información detallada de un usuario")
    @app_commands.describe(usuario="Usuario del que quieres ver la información")
    async def userinfo(self, ctx: commands.Context, usuario: Optional[discord.Member] = None):
        """Información detallada de un usuario — &userinfo [@usuario]"""
        user = usuario or ctx.author

        # Forzar la obtención del miembro si solo tenemos un User (caso raro)
        if isinstance(user, discord.User) and ctx.guild:
            member = ctx.guild.get_member(user.id) or user
        else:
            member = user

        roles = member.roles[1:]  # @everyone al inicio, lo omitimos
        roles_str = " ".join(r.mention for r in reversed(roles)) if roles else "Ninguno"
        if len(roles_str) > 1024:
            roles_str = roles_str[:1000] + "… y más"

        created_dt = member.created_at.replace(tzinfo=timezone.utc) if member.created_at else None
        joined_dt = member.joined_at.replace(tzinfo=timezone.utc) if hasattr(member, 'joined_at') and member.joined_at else None

        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            color=member.top_role.color if member.top_role.color.value != 0 else discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        embed.add_field(name="📛 Nombre global", value=member.name, inline=True)
        embed.add_field(name="🤖 Bot", value="Sí" if member.bot else "No", inline=True)

        if isinstance(member, discord.Member):
            voice_state = member.voice
            if voice_state and voice_state.channel:
                embed.add_field(name="🔊 En canal de voz", value=voice_state.channel.mention, inline=True)
            else:
                embed.add_field(name="🔊 En canal de voz", value="No", inline=True)

        embed.add_field(name="📅 Se unió al servidor", value=f"{self._format_date(joined_dt)}\n{self._format_date_relative(joined_dt)}", inline=False)
        embed.add_field(name="📆 Cuenta creada", value=f"{self._format_date(created_dt)}\n{self._format_date_relative(created_dt)}", inline=False)

        if isinstance(member, discord.Member):
            embed.add_field(name="🏆 Rol más alto", value=member.top_role.mention, inline=True)
            embed.add_field(name="🎨 Color del rol", value=str(member.top_role.color) if member.top_role.color.value != 0 else "Ninguno", inline=True)

        if isinstance(member, discord.Member):
            embed.add_field(name=f"📋 Roles ({len(roles)})", value=roles_str, inline=False)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="serverinfo", description="Muestra información detallada del servidor")
    async def serverinfo(self, ctx: commands.Context):
        """Información detallada del servidor — &serverinfo"""
        guild = ctx.guild
        if not guild:
            await ctx.send("❌ Este comando solo funciona en un servidor.", ephemeral=True)
            return

        created_dt = guild.created_at.replace(tzinfo=timezone.utc) if guild.created_at else None

        # Canales
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        forum_channels = len(guild.forum_channels) if hasattr(guild, 'forum_channels') else 0
        stage_channels = len(guild.stage_channels)
        total_channels = text_channels + voice_channels + forum_channels + stage_channels

        # Miembros
        members = guild.members
        humans = sum(1 for m in members if not m.bot)
        bots = sum(1 for m in members if m.bot)

        # Roles
        roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)
        roles_str = " ".join(r.mention for r in roles if r.name != "@everyone")
        if len(roles_str) > 1024:
            roles_str = roles_str[:1000] + "… y más"

        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc),
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if guild.banner:
            embed.set_image(url=guild.banner.url)

        owner = guild.owner
        embed.add_field(name="👑 Dueño", value=owner.mention if owner else "Desconocido", inline=True)
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="📅 Creado", value=f"{self._format_date(created_dt)}\n{self._format_date_relative(created_dt)}", inline=False)

        embed.add_field(name="👥 Miembros", value=f"**Total:** {guild.member_count}\n🙂 Humanos: {humans}\n🤖 Bots: {bots}", inline=True)
        embed.add_field(name="💬 Canales", value=f"**Total:** {total_channels}\n#️⃣ Texto: {text_channels}\n🔊 Voz: {voice_channels}", inline=True)
        if forum_channels:
            embed.add_field(name="📋 Foros", value=str(forum_channels), inline=True)

        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        embed.add_field(name="⭐ Mejoras", value=f"**Nivel:** {boost_level}\n**Impulsos:** {boost_count}", inline=True)

        embed.add_field(name=f"📋 Roles ({len(guild.roles) - 1})", value=roles_str or "Ninguno", inline=False)

        if guild.features:
            features_str = ", ".join(f"`{f}`" for f in guild.features[:10])
            if len(guild.features) > 10:
                features_str += f" … y {len(guild.features) - 10} más"
            embed.add_field(name="✨ Características", value=features_str, inline=False)

        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="avatar", description="Muestra el avatar de un usuario en tamaño completo")
    @app_commands.describe(usuario="Usuario del que quieres ver el avatar")
    async def avatar(self, ctx: commands.Context, usuario: Optional[discord.Member] = None):
        """Muestra el avatar de un usuario — &avatar [@usuario]"""
        user = usuario or ctx.author

        embed = discord.Embed(
            title=f"🖼️ Avatar de {user.display_name}",
            description=f"[Abrir en navegador]({user.display_avatar.url})",
            color=discord.Color.blurple(),
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="roleinfo", description="Muestra información detallada de un rol")
    @app_commands.describe(rol="Rol del que quieres ver la información")
    async def roleinfo(self, ctx: commands.Context, rol: discord.Role):
        """Información detallada de un rol — &roleinfo @rol"""
        created_dt = rol.created_at.replace(tzinfo=timezone.utc) if rol.created_at else None

        color_hex = str(rol.color) if rol.color.value != 0 else "Ninguno"
        color_display = rol.color if rol.color.value != 0 else discord.Color.default()

        embed = discord.Embed(
            title=f"📋 Información del rol: {rol.name}",
            color=color_display,
            timestamp=datetime.now(timezone.utc),
        )

        embed.add_field(name="🆔 ID", value=rol.id, inline=True)
        embed.add_field(name="🎨 Color", value=color_hex, inline=True)
        embed.add_field(name="📌 Posición", value=rol.position, inline=True)

        embed.add_field(name="👥 Miembros con este rol", value=len(rol.members), inline=True)
        embed.add_field(name="📅 Creado", value=f"{self._format_date(created_dt)}\n{self._format_date_relative(created_dt)}", inline=False)

        # Mostrar si se menciona por separado y si es administrador
        embed.add_field(name="🔧 Adminsitrador", value="Sí" if rol.permissions.administrator else "No", inline=True)
        embed.add_field(name="🔔 Mencionable", value="Sí" if rol.mentionable else "No", inline=True)
        embed.add_field(name="👁️ Mostrado por separado", value="Sí" if rol.hoist else "No", inline=True)

        # Mostrar algunos permisos importantes si los tiene
        important_perms = {
            "manage_server": "Administrar servidor",
            "manage_roles": "Administrar roles",
            "manage_channels": "Administrar canales",
            "manage_messages": "Administrar mensajes",
            "kick_members": "Expulsar miembros",
            "ban_members": "Banear miembros",
            "moderate_members": "Moderar miembros",
        }

        perms_list = []
        for perm_key, perm_name in important_perms.items():
            if getattr(rol.permissions, perm_key, False):
                perms_list.append(f"✅ {perm_name}")

        if perms_list:
            embed.add_field(name="⚡ Permisos destacados", value="\n".join(perms_list[:8]), inline=False)

        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ping", description="Muestra la latencia del bot")
    async def ping(self, ctx: commands.Context):
        """Muestra la latencia del bot — &ping"""
        latency = round(self.bot.latency * 1000)

        # Determinar color según latencia
        if latency < 100:
            color = discord.Color.green()
            emoji = "🟢"
        elif latency < 250:
            color = discord.Color.orange()
            emoji = "🟡"
        else:
            color = discord.Color.red()
            emoji = "🔴"

        embed = discord.Embed(
            title="🏓 ¡Pong!",
            description=f"{emoji} **Latencia:** {latency}ms",
            color=color,
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="botinfo", description="Muestra información detallada del bot")
    async def botinfo(self, ctx: commands.Context):
        """Información detallada del bot — &botinfo"""
        bot = self.bot

        # Estadísticas
        total_servers = len(bot.guilds)
        total_users = sum(g.member_count or 0 for g in bot.guilds)
        total_channels = sum(len(g.channels) for g in bot.guilds)

        # Ping
        ping_ms = round(bot.latency * 1000)

        # Cogs cargados
        cogs_list = [f"`{cog}`" for cog in bot.cogs.keys()]
        cogs_str = ", ".join(cogs_list[:15])
        if len(cogs_list) > 15:
            cogs_str += f" … y {len(cogs_list) - 15} más"

        embed = discord.Embed(
            title=f"🤖 {bot.user.name} — Información",
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc),
        )

        if bot.user:
            embed.set_thumbnail(url=bot.user.display_avatar.url)

        embed.add_field(name="📡 Servidores", value=f"**{total_servers}** servidores", inline=True)
        embed.add_field(name="👥 Usuarios", value=f"**{total_users}** usuarios", inline=True)
        embed.add_field(name="💬 Canales", value=f"**{total_channels}** canales", inline=True)

        embed.add_field(name="⏱️ Tiempo activo", value=self._uptime, inline=True)
        embed.add_field(name="🏓 Latencia", value=f"**{ping_ms}ms**", inline=True)
        embed.add_field(name="📦 Versión de Discord.py", value=f"`{discord.__version__}`", inline=True)

        embed.add_field(name="⚙️ Cogs cargados", value=cogs_str, inline=False)

        embed.add_field(name="🆔 ID del Bot", value=bot.user.id if bot.user else "Desconocido", inline=True)
        embed.add_field(name="📅 Iniciado", value=f"<t:{int(self.start_time.timestamp())}:R>", inline=True)

        # Comandos
        total_commands = len(bot.commands)
        embed.add_field(name="📋 Comandos", value=f"**{total_commands}** comandos disponibles", inline=False)

        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)


    @commands.hybrid_command(name="banner", description="Muestra el banner de perfil de un usuario")
    @app_commands.describe(usuario="Usuario del que quieres ver el banner")
    async def banner(self, ctx: commands.Context, usuario: Optional[discord.Member] = None):
        """Muestra el banner de perfil de un usuario"""
        usuario = usuario or ctx.author

        if usuario.banner:
            embed = discord.Embed(
                title=f"🖼️ Banner de {usuario.display_name}",
                color=usuario.color or discord.Color.blurple(),
            )
            embed.set_image(url=usuario.banner.url)
            embed.set_footer(text=f"ID: {usuario.id}")
            await ctx.send(embed=embed)
        else:
            # Intentar obtener via API
            try:
                user_data = await self.bot.http.get_user(usuario.id)
                banner_id = user_data.get("banner")
                if banner_id:
                    is_animated = banner_id.startswith("a_")
                    fmt = "gif" if is_animated else "png"
                    url = f"https://cdn.discordapp.com/banners/{usuario.id}/{banner_id}.{fmt}?size=1024"
                    embed = discord.Embed(
                        title=f"🖼️ Banner de {usuario.display_name}",
                        color=usuario.color or discord.Color.blurple(),
                    )
                    embed.set_image(url=url)
                    embed.set_footer(text=f"ID: {usuario.id}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❌ **{usuario.display_name}** no tiene banner de perfil.")
            except:
                await ctx.send(f"❌ **{usuario.display_name}** no tiene banner de perfil.")

    @commands.hybrid_command(name="channelinfo", description="Muestra información detallada de un canal")
    @app_commands.describe(canal="Canal a inspeccionar (omite para el actual)")
    async def channelinfo(self, ctx: commands.Context, canal: Optional[discord.TextChannel] = None):
        """Muestra información de un canal del servidor"""
        canal = canal or ctx.channel

        embed = discord.Embed(
            title=f"📢 #{canal.name}",
            color=discord.Color.blurple(),
        )

        embed.add_field(name="ID", value=canal.id, inline=True)
        embed.add_field(name="Tipo", value=str(canal.type).title(), inline=True)
        embed.add_field(name="Categoría", value=canal.category.name if canal.category else "Sin categoría", inline=True)
        embed.add_field(name="Posición", value=canal.position, inline=True)
        embed.add_field(name="NSFW", value="Sí ⛔" if canal.is_nsfw() else "No ✅", inline=True)

        if hasattr(canal, "slowmode_delay"):
            embed.add_field(name="Modo lento", value=f"{canal.slowmode_delay}s" if canal.slowmode_delay else "Desactivado", inline=True)

        if isinstance(canal, discord.TextChannel):
            embed.add_field(name="Tópico", value=canal.topic[:200] if canal.topic else "Sin tópico", inline=False)

        embed.set_footer(text=f"Creado el {canal.created_at.strftime('%d/%m/%Y')}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="servericon", description="Muestra el icono del servidor en tamaño completo")
    async def servericon(self, ctx: commands.Context):
        """Muestra el icono del servidor"""
        if ctx.guild.icon:
            embed = discord.Embed(
                title=f"🖼️ Icono de {ctx.guild.name}",
                color=discord.Color.blurple(),
            )
            embed.set_image(url=ctx.guild.icon.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Este servidor no tiene icono.")

    @commands.hybrid_command(name="invite", description="Obtén el enlace de invitación de Mint Bot")
    async def invite(self, ctx: commands.Context):
        """Invita a Mint Bot a tu servidor"""
        embed = discord.Embed(
            title="🔗 Invitar a Mint Bot",
            description=(
                "¿Quieres invitarme a otro servidor?\n\n"
                f"[**Haz clic aquí para invitarme**]"
                f"(https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)\n\n"
                "Gracias por tenerme en tu servidor 💚"
            ),
            color=discord.Color.green(),
        )
        embed.set_footer(text="Mint Bot — Inspirado en NTE")
        await ctx.send(embed=embed)


async def setup(bot):
    """Carga el cog Info en el bot"""
    if bot.get_cog("Info") is not None:
        return
    await bot.add_cog(Info(bot))

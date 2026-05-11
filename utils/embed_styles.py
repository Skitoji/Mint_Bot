import discord

def simple(title, desc, color=discord.Color.blurple()):
    embed = discord.Embed(title=title, description=desc, color=color)
    return embed

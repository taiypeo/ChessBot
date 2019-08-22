import discord
from discord.ext import commands

from ... import database


def get_full_username(user: discord.User) -> str:
    return f"{user.name}#{user.discriminator}"


def get_user(bot: commands.Bot, user: database.User) -> discord.User:
    return bot.get_user(user.discord_id)

import discord
from discord.ext import commands

from ... import database


def get_database_user(user_id: int) -> database.User:
    user = database.session.query(database.User).filter_by(discord_id=user_id).first()
    if user is None:
        raise RuntimeError(f"User #{user_id} is not present in the database")

    return user


def get_full_username(user: discord.User) -> str:
    return f"{user.name}#{user.discriminator}"


def get_discord_user(bot: commands.Bot, user: database.User) -> discord.User:
    return bot.get_user(user.discord_id)


def create_database_user(discord_user: discord.User) -> database.User:
    if (
        database.session.query(database.User)
        .filter_by(discord_id=discord_user.id)
        .first()
        is not None
    ):
        raise RuntimeError(f"User #{discord_user.id} already exists")

    user = database.User(
        discord_id=discord_user.id, username=get_full_username(discord_user)
    )
    database.add_to_database(user)

    return user

import discord
from discord.ext import commands
from loguru import logger

from .game_utils import get_game, update_game
from .user_utils import get_database_user, create_database_user
from ... import database


async def get_game_ctx(
    ctx: commands.Context, user_id: int, game_id: int
) -> database.Game:
    try:
        game = get_game(user_id, game_id)
    except RuntimeError as err:
        if game_id is None:
            await ctx.send(f"{ctx.author.mention}, you don't have a last game.")
        else:
            await ctx.send(f"{ctx.author.mention}, couldn't find that game.")

        logger.error(err)
        return None

    logger.info(f"Got a game - {game}")

    update_game(game)
    return game


async def get_author_user_ctx(ctx: commands.Context) -> database.User:
    try:
        user = get_database_user(ctx.author.id)
        return user
    except RuntimeError as err:
        logger.error(err)
        await ctx.send(
            f"{ctx.author.mention}, failed to fetch your data from the database. Please, contact the admin."
        )
        return None


async def create_database_user_ctx(
    ctx: commands.Context, discord_user: discord.User
) -> database.User:
    try:
        database_user = create_database_user(discord_user)
    except RuntimeError as err:
        logger.info(err)  # not an error, the user already exists

        try:
            database_user = get_database_user(discord_user.id)
        except RuntimeError as err:
            logger.error(err)
            await ctx.send(
                f"{discord_user.mention}, failed to find you in the database. Please, contact the admin."
            )
            return None

    return database_user

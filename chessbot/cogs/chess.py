import traceback
import discord
from discord.ext import commands
from loguru import logger
from .utils import (
    get_game,
    get_game_status,
    update_game,
    get_database_user,
    handle_draw_accept,
)
from .. import database


class Chess(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def status_func(
        self, ctx: commands.Context, game_id: int = None, game: database.Game = None
    ) -> None:
        if game is None:
            try:
                game = get_game(ctx.author.id, game_id)
            except RuntimeError as err:
                if game_id is None:
                    await ctx.send(f"{ctx.author.mention}, you don't have a last game.")
                else:
                    await ctx.send(f"{ctx.author.mention}, couldn't find that game.")

                logger.error(err)
                return

            logger.info(f"Got game #{game_id} - {game}")
            update_game(game)

        try:
            status_str, img = get_game_status(self.bot, game)
        except RuntimeError as err:
            await ctx.send(
                f"{ctx.author.mention}, failed to get the status for that game. Please contact the admin."
            )

            logger.error(err)
            return

        logger.info(f"Sent the status for game #{game.id}")
        await ctx.send(status_str, file=img)

    @commands.command()
    async def status(self, ctx: commands.Context, game_id: int = None) -> None:
        logger.info("Got a !status command")
        await self.status_func(ctx, game_id=game_id)

    @commands.command()
    async def accept(self, ctx: commands.Context, game_id: int = None) -> None:
        logger.info("Got an !accept command")

        try:
            game = get_game(ctx.author.id, game_id)
        except RuntimeError as err:
            if game_id is None:
                await ctx.send(f"{ctx.author.mention}, you don't have a last game.")
            else:
                await ctx.send(f"{ctx.author.mention}, couldn't find that game.")

            logger.error(err)
            return

        logger.info(f"Got game #{game_id} - {game}")

        if game.draw_proposed and game.white_accepted_draw != game.black_accepted_draw:
            try:
                user = get_database_user(ctx.author.id)
            except RuntimeError as err:
                logger.error(err)
                await ctx.send(
                    f"{ctx.author.mention}, failed to fetch your data from the database. Please, contact the admin."
                )

                return

            try:
                handle_draw_accept(user, game)
            except RuntimeError as err:
                logger.error(err)
                await ctx.send(
                    f"{ctx.author.mention}, you can't accept your own draw offer."
                )

                return

            await self.status_func(ctx, game=game)
        else:
            await ctx.send(
                f"{ctx.author.mention}, there is nothing to accept for this game."
            )
            logger.error(f"Nothing to accept for game #{game.id}")

    @commands.command()
    async def play(self, ctx: commands.Context, user: discord.Member) -> None:
        pass

    @commands.command()
    async def move(self, ctx: commands.Context, pgn: str, san_move: str) -> None:
        pass

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger.error(error)
        logger.error(traceback.format_exc())
        await ctx.send(f"{ctx.author.mention}, {error}")

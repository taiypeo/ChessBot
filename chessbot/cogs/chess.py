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
    handle_turn_check,
    handle_move,
)
from .. import database


class Chess(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def get_game(
        self, ctx: commands.Context, user_id: int, game_id: int
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

    async def get_author_user(self, ctx: commands.Context) -> database.User:
        try:
            user = get_database_user(ctx.author.id)
            return user
        except RuntimeError as err:
            logger.error(err)
            await ctx.send(
                f"{ctx.author.mention}, failed to fetch your data from the database. Please, contact the admin."
            )
            return None

    async def status_func(
        self, ctx: commands.Context, game_id: int = None, game: database.Game = None
    ) -> None:
        if game is None:
            game = await self.get_game(ctx, ctx.author.id, game_id)
            if game is None:
                return

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

        game = await self.get_game(ctx, ctx.author.id, game_id)
        if game is None:
            return

        if game.draw_proposed and game.white_accepted_draw != game.black_accepted_draw:
            user = await self.get_author_user(ctx)
            if user is None:
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
    async def move(
        self, ctx: commands.Context, san_move: str, game_id: int = None
    ) -> None:
        logger.info("Got a !move command")

        game = await self.get_game(ctx, ctx.author.id, game_id)
        if game is None:
            return

        if game.winner is not None:
            await ctx.send(f"{ctx.author.mention}, the game is over.")
            logger.error(f"Can't move in game #{game.id} - the game is over")

            return

        user = await self.get_author_user(ctx)
        if user is None:
            return

        try:
            handle_turn_check(user, game)
        except RuntimeError as err:
            logger.error(err)
            await ctx.send(f"{ctx.author.mention}, it is not your turn.")
            return

        try:
            handle_move(game, san_move)
        except ValueError as err:
            logger.error(err)
            await ctx.send(
                f"{ctx.author.mention}, {san_move} is not a valid SAN move in this game."
            )
            return

        update_game(game, recalculate_expiration_date=True, reset_draw_offer=True)
        user.last_game = game
        await self.status_func(ctx, game=game)

    @commands.command()
    async def play(self, ctx: commands.Context, user: discord.Member) -> None:
        pass

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger.error(error)
        logger.error(traceback.format_exc())
        await ctx.send(f"{ctx.author.mention}, {error}")

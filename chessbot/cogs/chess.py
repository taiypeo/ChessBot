import traceback
import discord
from discord.ext import commands
from loguru import logger
from .utils import (
    get_game,
    get_game_status,
    update_game,
    get_database_user,
    is_player,
    handle_action_offer,
    handle_action_accept,
    handle_turn_check,
    handle_move,
    create_database_user,
)
from .. import database, constants


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

    async def create_database_user(
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

    async def status_func(
        self, ctx: commands.Context, game_id: int = None, game: database.Game = None
    ) -> None:
        if game is None:
            game = await self.get_game(ctx, ctx.author.id, game_id)
            if game is None:  # check the Game object for validity
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
        if game is None:  # check the Game object for validity
            return

        user = await self.get_author_user(ctx)
        if user is None:  # check the User object for validity
            return

        if not is_player(
            game, user
        ):  # check that the message author is a player in this game
            logger.error(
                f"User #{user.discord_id} tried to illegally !accept in game #{game.id}"
            )
            await ctx.send(f"{ctx.author.mention}, you can't use !accept in this game.")
            return

        if game.white_accepted_action != game.black_accepted_action:
            try:
                handle_action_accept(user, game)
            except RuntimeError as err:
                logger.error(err)
                await ctx.send(
                    f"{ctx.author.mention}, you can't accept your own actions."
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
        if game is None:  # check the Game object for validity
            return

        if game.winner is not None:  # check that the game hasn't finished yet
            await ctx.send(f"{ctx.author.mention}, the game is over.")
            logger.error(f"Can't move in game #{game.id} - the game is over")
            return

        user = await self.get_author_user(ctx)
        if user is None:  # check the User object for validity
            return

        if not is_player(
            game, user
        ):  # check that the message author is a player in this game
            logger.error(
                f"User #{user.discord_id} tried to illegally play game #{game.id}"
            )
            await ctx.send(f"{ctx.author.mention}, you can't play this game.")
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

        update_game(game, recalculate_expiration_date=True, reset_action=True)
        user.last_game = game
        await self.status_func(ctx, game=game)

    @commands.command()
    async def draw(self, ctx: commands.Context, game_id: int = None) -> None:
        logger.info("Got a !draw command")

        game = await self.get_game(ctx, ctx.author.id, game_id)
        if game is None:  # check the Game object for validity
            return

        if game.winner is not None:  # check that the game hasn't finished yet
            await ctx.send(f"{ctx.author.mention}, the game is over.")
            logger.error(f"Can't offer draw in game #{game.id} - the game is over")
            return

        user = await self.get_author_user(ctx)
        if user is None:  # check the User object for validity
            return

        if not is_player(
            game, user
        ):  # check that the message author is a player in this game
            logger.error(
                f"User #{user.discord_id} tried to illegally offer a draw in game #{game.id}"
            )
            await ctx.send(
                f"{ctx.author.mention}, you can't offer a draw in this game."
            )
            return

        if (
            game.action_proposed == constants.ACTION_DRAW
        ):  # check that a draw hasn't been offered yet
            logger.error(f"Draw has already been offered in game #{game.id}")
            await ctx.send(
                f"{ctx.author.mention}, a draw has already been offered in this game."
            )
            return

        try:
            handle_action_offer(user, game, constants.ACTION_DRAW)
        except RuntimeError as err:
            logger.error(err)
            await ctx.send(
                f"{ctx.author.mention}, you can't offer a draw in this game."
            )
            return

        update_game(game)
        await self.status_func(ctx, game=game)

    @commands.command()
    async def play(self, ctx: commands.Context, user: discord.Member) -> None:
        white = await self.create_database_user(ctx.author)
        black = await self.create_database_user(user)

        if white is None or black is None:  # check the validity of User objects
            return

        if white == black:  # check that white and black are different users
            logger.error(f"User #{white.discord_id} tried to play against themselves")
            await ctx.send(f"{ctx.author.mention}, you can't play against yourself.")
            return

        game = database.Game(white=white, black=black)
        database.add_to_database(game)

        white.last_game = game
        database.add_to_database(white)

        black.last_game = game
        database.add_to_database(black)

        await self.status_func(ctx, game=game)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger.error(error)
        logger.error(traceback.format_exc())
        await ctx.send(f"{ctx.author.mention}, {error}")

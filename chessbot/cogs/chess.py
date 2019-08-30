import traceback
import discord
from discord.ext import commands
from loguru import logger
from .utils import (
    get_game_ctx,
    get_author_user_ctx,
    create_database_user_ctx,
    get_game_status,
    update_game,
    is_player,
    which_player,
    handle_action_offer,
    handle_action_accept,
    handle_turn_check,
    handle_move,
    update_ongoing_games,
)
from .. import database, constants


class Chess(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def status_func(
        self, ctx: commands.Context, game_id: int = None, game: database.Game = None
    ) -> None:
        if game is None:
            game = await get_game_ctx(ctx, ctx.author.id, game_id)
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

        game = await get_game_ctx(ctx, ctx.author.id, game_id)
        if game is None:  # check the Game object for validity
            return

        user = await get_author_user_ctx(ctx)
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

            user.last_game = game
            database.add_to_database(user)
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

        game = await get_game_ctx(ctx, ctx.author.id, game_id)
        if game is None:  # check the Game object for validity
            return

        if game.winner is not None:  # check that the game hasn't finished yet
            await ctx.send(f"{ctx.author.mention}, the game is over.")
            logger.error(f"Can't move in game #{game.id} - the game is over")
            return

        user = await get_author_user_ctx(ctx)
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
        database.add_to_database(user)
        await self.status_func(ctx, game=game)

    @commands.command()
    async def offer(
        self, ctx: commands.Context, action: str, game_id: int = None
    ) -> None:
        logger.info("Got an !offer command")

        game = await get_game_ctx(ctx, ctx.author.id, game_id)
        if game is None:  # check the Game object for validity
            return

        if game.winner is not None:  # check that the game hasn't finished yet
            await ctx.send(f"{ctx.author.mention}, the game is over.")
            logger.error(f"Can't offer an action in game #{game.id} - the game is over")
            return

        user = await get_author_user_ctx(ctx)
        if user is None:  # check the User object for validity
            return

        if not is_player(
            game, user
        ):  # check that the message author is a player in this game
            logger.error(
                f"User #{user.discord_id} tried to illegally offer an in game #{game.id}"
            )
            await ctx.send(
                f"{ctx.author.mention}, you can't offer an action in this game."
            )
            return

        action_type = constants.OFFERABLE_ACTIONS.get(action.upper())

        if action_type is None:  # check that this action is offerable
            logger.error(
                f'User #{user.discord_id} tried to offer an illegal action "{action}" in game #{game.id}'
            )
            await ctx.send(f"{ctx.author.mention}, this action does not exist.")
            return

        if (
            game.action_proposed == action_type
        ):  # check that this action hasn't been offered yet
            logger.error(
                f'Action "{action}" has already been offered in game #{game.id}'
            )
            await ctx.send(
                f"{ctx.author.mention}, this action has already been offered in this game."
            )
            return

        try:
            handle_action_offer(user, game, action_type)
        except RuntimeError as err:
            logger.error(err)
            await ctx.send(
                f"{ctx.author.mention}, you can't offer an action in this game."
            )
            return

        update_game(game)
        user.last_game = game
        database.add_to_database(user)
        await self.status_func(ctx, game=game)

    @commands.command()
    async def play(self, ctx: commands.Context, user: discord.Member) -> None:
        white = await create_database_user_ctx(ctx, ctx.author)
        black = await create_database_user_ctx(ctx, user)

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

    @commands.command()
    async def concede(self, ctx: commands.Context, game_id: int = None) -> None:
        logger.info("Got a !concede command")

        game = await get_game_ctx(ctx, ctx.author.id, game_id)
        if game is None:  # check the Game object for validity
            return

        if game.winner is not None:  # check that the game hasn't finished yet
            await ctx.send(f"{ctx.author.mention}, the game is over.")
            logger.error(f"Can't concede in game #{game.id} - the game is over")
            return

        user = await get_author_user_ctx(ctx)
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

        update_game(game, concede_side=which_player(game, user))
        user.last_game = game
        database.add_to_database(user)
        await self.status_func(ctx, game=game)

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        logger.info("Updating all ongoing games")
        update_ongoing_games()

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger.error(error)
        logger.error(traceback.format_exc())
        await ctx.send(f"{ctx.author.mention}, {error}")

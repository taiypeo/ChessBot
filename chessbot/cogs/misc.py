import traceback
from discord.ext import commands
from .utils import get_author_user_ctx, get_vs_line, update_game
from .. import database

from loguru import logger


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def games(self, ctx: commands.Context, all: str = "") -> None:
        logger.info("Got a !games command")

        user = await get_author_user_ctx(ctx)
        if user is None:  # check the User object for validity
            return

        for game in user.games:
            update_game(game)

        games = user.ongoing_games
        if all.lower() == "all":
            games = [*games, *user.finished_games]

        outputs = []
        for game in games:
            vs_line = get_vs_line(self.bot, game)
            status = "Ongoing" if game.winner is None else "Finished"
            game_output = f"**[{game.id}]** {vs_line}\t*Status: {status}*."

            outputs.append(game_output)

        output = "\n".join(outputs)
        if output == "":
            output = f"{ctx.author.mention}, you don't have any games."
        else:
            output = f"{ctx.author.mention}, your games:\n\n{output}"
        await ctx.send(output)

    @commands.command()
    async def elo(self, ctx: commands.Context) -> None:
        logger.info("Got an !elo command")

        user = await get_author_user_ctx(ctx)
        if user is None:  # check the User object for validity
            return
        if user.elo is None:
            logger.error(f"User #{user.discord_id} does not have an elo rating")
            await ctx.send(
                f"{ctx.author.mention}, you don't have an elo rating. Please, contact the admin."
            )
            return

        await ctx.send(
            f"{ctx.author.mention}, your current elo rating is *{user.elo}*."
        )

    @commands.command()
    async def leaderboard(self, ctx: commands.Context, top: int = 10) -> None:
        logger.info("Got a !leaderboard command")

        if top < 3 or top > 50:
            logger.error(f"{top} is an invalid value for top in !leaderboard")
            await ctx.send(
                f'{ctx.author.mention}, choose another value of "Top *N*", please.'
            )
            return

        outputs = []
        users = (
            database.session.query(database.User)
            .order_by(database.User.elo.desc())
            .limit(top)
        )
        for i, user in enumerate(users):
            username = user.username or user.discord_id
            user_output = f"**[{i + 1}]** {username} - {user.elo} elo."
            outputs.append(user_output)

        output = "\n".join(outputs)
        if output == "":
            output = f"{ctx.author.mention}, there aren't any players in the leaderboard yet."
        else:
            output = f"__Global leaderboard:__\n\n{output}"
        await ctx.send(output)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger.error(error)
        logger.error(traceback.format_exc())
        await ctx.send(f"{ctx.author.mention}, {error}")

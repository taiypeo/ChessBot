from discord.ext import commands
from .utils import get_author_user_ctx, get_vs_line, update_game

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

import discord
from discord.ext import commands
from loguru import logger
from .utils import get_game, get_game_status
from .. import database


class Chess(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def play(self, ctx: commands.Context, user: discord.Member) -> None:
        pass

    @commands.command()
    async def status(self, ctx: commands.Context, game_id: int = None) -> None:
        game = get_game(ctx, game_id)
        if game is None:
            if game_id is None:
                await ctx.send(f"{ctx.author.mention}, you don't have a last game.")
            else:
                await ctx.send(f"{ctx.author.mention}, couldn't find that game.")
        else:
            status_str, img = get_game_status(self.bot, game)
            if status_str is None:
                await ctx.send(
                    f"{ctx.author.mention}, failed to get the status for that game. Please contact the admin."
                )
            else:
                logger.info(f"Sent the status for game #{game.id}")
                await ctx.send(status_str, file=img)

    @commands.command()
    async def move(self, ctx: commands.Context, pgn: str, san_move: str) -> None:
        pass

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger.error(error)
        await ctx.send(f"{ctx.author.mention}, {error}")

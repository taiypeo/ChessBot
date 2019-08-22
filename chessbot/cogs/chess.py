import discord
from discord.ext import commands
from loguru import logger
from .utils import load_from_pgn, save_to_pgn, move, to_png, get_game, get_game_status
from .. import database


class Chess(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def play(self, ctx: commands.Context, user: discord.Member) -> None:
        await ctx.send(f"PING! {user.mention}")

    @commands.command()
    async def status(self, ctx: commands.Context, game_id: int = None) -> None:
        game = get_game(ctx, game_id)
        if game is None:
            logger.error(f"No game found for {ctx.author.id}")

            if game_id is None:
                await ctx.send(f"{ctx.author.mention}, you don't have a last game.")
            else:
                await ctx.send(f"{ctx.author.mention}, couldn't find that game.")
        else:
            status_str, img = get_game_status(self.bot, game)
            if status_str is None:
                await ctx.send(f"{ctx.author.mention}, failed to get the status for that game. Please contact the admin.")
            else:
                await ctx.send(status_str, file=img)

    @commands.command()
    async def move(self, ctx: commands.Context, pgn: str, san_move: str) -> None:
        board = load_from_pgn(pgn)
        try:
            move(board, san_move)
        except ValueError:
            await ctx.send(f"Invalid SAN move specified.")
            return

        svg = discord.File(to_svg(board), filename="board.png")
        new_pgn = save_to_pgn(board)

        await ctx.send(new_pgn, file=svg)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger.error(error)
        await ctx.send(f"{ctx.author.mention}, {error}")
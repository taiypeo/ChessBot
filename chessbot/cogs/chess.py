from discord import File
from discord.ext import commands
from loguru import logger
from .utils import load_from_pgn, save_to_pgn, move, to_svg


class Chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def move(self, ctx: commands.Context, pgn: str, san_move: str) -> None:
        board = load_from_pgn(pgn)
        try:
            move(board, san_move)
        except ValueError:
            await ctx.send(f"Invalid SAN move specified.")
            return

        svg = File(to_svg(board), filename="board.png")
        new_pgn = save_to_pgn(board)

        await ctx.send(new_pgn, file=svg)

    @move.error
    async def move_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        logger.error(error)
        await ctx.send(f"Error: {error}")

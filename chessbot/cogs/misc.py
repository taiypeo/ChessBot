from discord.ext import commands
from .. import database


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    def games(self, ctx: commands.Context, all: str = "") -> None:
        pass

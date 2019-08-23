import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def help(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title="ChessBot v0.1",
            url="https://github.com/QwertygidQ/ChessBot",
            description="A chess bot for Discord, made with discord.py and python-chess.",
            color=0x88E93A,
        )
        embed.set_author(name="Qwertygid", url="https://github.com/QwertygidQ/")
        embed.add_field(name="!help", value="Displays the help message.", inline=False)
        embed.add_field(
            name="!play @someone", value="Starts a game with @someone.", inline=False
        )
        embed.add_field(
            name="!move (SAN move) [Game ID]",
            value="Moves a piece according to the standard algebraic notation in the game.",
            inline=False,
        )
        embed.add_field(
            name="!status [Game ID]",
            value="Displays the current status of the game.",
            inline=False,
        )
        embed.add_field(
            name="!draw [Game ID]", value="Offers a draw in the game.", inline=False
        )
        embed.add_field(
            name="!accept [Game ID]", value="Accepts a draw in the game.", inline=False
        )
        embed.set_footer(
            text="This bot is still under development, expect many things to change."
        )

        await ctx.send(embed=embed)

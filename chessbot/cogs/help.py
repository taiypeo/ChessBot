import discord
from discord.ext import commands
from loguru import logger


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def help(self, ctx: commands.Context) -> None:
        logger.info("Got a !help command")

        prefix = self.bot.command_prefix
        embed = discord.Embed(
            title="ChessBot v0.4",
            url="https://github.com/QwertygidQ/ChessBot",
            description="A chess bot for Discord, made with discord.py and python-chess.",
            color=0x88E93A,
        )
        embed.set_author(name="Qwertygid", url="https://github.com/QwertygidQ/")
        embed.add_field(
            name=f"{prefix}help", value="Displays the help message.", inline=False
        )
        embed.add_field(
            name=f"{prefix}play @someone",
            value="Starts a game with @someone.",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}move (SAN move) [Game ID]",
            value="Moves a piece according to the standard algebraic notation in the game.",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}status [Game ID]",
            value="Displays the current status of the game.",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}offer (Action) [Game ID]",
            value="Offers an action in the game. Possible actions: *draw, undo*.",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}accept [Game ID]",
            value="Accepts an action in the game.",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}concede [Game ID]",
            value="Concedes in the game.",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}games [*all*]", value="Shows your games.", inline=False
        )
        embed.add_field(
            name=f"{prefix}elo", value="Shows your elo rating.", inline=False
        )
        embed.add_field(
            name=f"{prefix}leaderboard [Top *N*]",
            value="Shows the global leaderboard (3 ≤ N ≤ 50).",
            inline=False,
        )
        embed.set_footer(
            text="This bot is still under development, expect many things to change."
        )

        await ctx.send(embed=embed)

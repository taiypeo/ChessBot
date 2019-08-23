from discord.ext import commands
from loguru import logger
from .cogs.chess import Chess
from .cogs.help import Help
from .config import TOKEN

bot = commands.Bot(command_prefix="/")
bot.remove_command("help")  # remove the default !help command
bot.add_cog(Chess(bot))
bot.add_cog(Help(bot))


@bot.event
async def on_ready() -> None:
    logger.info(f"Logged in as {bot.user}")


def main() -> None:
    bot.run(TOKEN)

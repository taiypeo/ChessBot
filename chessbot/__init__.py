import discord
from loguru import logger
from .config import TOKEN

client = discord.Client()


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")


@client.event
async def on_message(msg):
    if message.author == client.user:
        return

    if message.content.startsWith("/hello"):
        await message.channel.send("Hello!")


def main():
    client.run(TOKEN)

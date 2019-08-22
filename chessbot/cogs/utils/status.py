import discord
from discord.ext import commands
from loguru import logger
from typing import Tuple

from .chess_functions import load_from_pgn, to_png
from .user import get_user
from ... import database


def get_game(ctx: commands.Context, game_id: int) -> database.Game:
    user_id = ctx.author.id

    if game_id is None:
        game = (
            database.session.query(database.User).filter_by(discord_id=user_id).first()
        )
    else:
        game = database.session.query(database.Game).get(game_id)

    if game is not None:
        if game_id is None:
            game = game.last_game

        return game

    return None


def _get_status_mentions(white: discord.User, black: discord.User, game: database.Game) -> Tuple[str, str]:
    if white is None:
        white_mention = game.white.username or game.white.discord_id
    else:
        white_mention = white.mention

    if black is None:
        black_mention = game.black.username or game.black.discord_id
    else:
        black_mention = black.mention

    return white_mention, black_mention


def get_game_status(bot: commands.Bot, game: database.Game) -> Tuple[str, discord.File]:
    if not game.white or not game.black:
        logger.error(f"Either white or black player is not present in game #{game.id}")
        return None, None

    white, black = get_user(bot, game.white), get_user(bot, game.black)
    white_mention, black_mention = _get_status_mentions(white, black, game)

    board = load_from_pgn(game.pgn)

    status = f"Game ID: {game.id}\n" \
        f"{white_mention} (white) **VS.** {black_mention} (black)"

    return status, to_png(board)
import datetime
import discord
from discord.ext import commands
from loguru import logger
from typing import Tuple

from .chess_functions import load_from_pgn, to_png, get_winner
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

    logger.error(f"No game found for {user_id}")
    return None


def _get_status_mentions(
    white: discord.User, black: discord.User, game: database.Game
) -> Tuple[str, str]:
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
    turn = "White" if board.turn else "Black"
    expired = datetime.datetime.now() > game.expiration_date
    game_over = expired or board.is_game_over()  # TODO: add claim_draw

    status = (
        f"__Game ID: {game.id}__\n"
        f"{white_mention} (white) **VS.** {black_mention} (black)\n"
    )
    if not game_over:
        status += (
            f"*{turn}'s turn.*\n\n"
            f"This game will expire on {game.expiration_date},\nresulting in {turn} losing, if they don't make a move."
        )
    else:
        if game.winner == database.WHITE:
            result = "White wins."
        elif game.winner == database.BLACK:
            result = "Black wins."
        elif game.winner == database.DRAW:
            result = "Draw."
        else:
            logger.error(f"Game winner is None in game #{game.id}")
            result = get_winner(board)  # TODO: add claim_draw

        if result is None:
            logger.error(f"Game is over but there is no result!")
            return None, None

        status += f"\n**Game over!** {result}"

    return status, to_png(board)

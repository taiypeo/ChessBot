import discord
from discord.ext import commands
from typing import Tuple

from .chess_utils import load_from_pgn, to_png, get_turn
from .user_utils import get_user
from ... import database, constants


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
        raise RuntimeError(
            f"Either white or black player is not present in game #{game.id}"
        )

    white, black = get_user(bot, game.white), get_user(bot, game.black)
    white_mention, black_mention = _get_status_mentions(white, black, game)

    status = (
        f"__Game ID: {game.id}__\n"
        f"{white_mention} (White) **VS.** {black_mention} (Black)\n"
    )

    board = load_from_pgn(game.pgn)

    if game.winner is None and game.win_reason is None:
        turn = get_turn(board)
        turn_str = constants.turn_to_str(turn)
        status += (
            f"*{turn_str.capitalize()}'s turn.*\n\n"
            f"This game will expire on {game.expiration_date},\nresulting in {turn_str} losing, if they don't make a move."
        )
    elif game.winner is not None and game.win_reason is not None:
        result = constants.turn_to_str(game.winner).capitalize()
        result = (
            f"{result} wins - {game.win_reason}."
            if game.winner != constants.DRAW
            else game.win_reason + "."
        )

        status += f"\n**Game over!** {result}"
    else:
        raise RuntimeError(
            f"Either game.winner or game.win_reason is not present in game #{game.id}"
        )

    return status, to_png(board)

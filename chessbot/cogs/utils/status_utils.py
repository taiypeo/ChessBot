import discord
from discord.ext import commands
from loguru import logger
from typing import Tuple

from .chess_utils import load_from_pgn, to_png, get_winner, get_game_over_reason
from .user_utils import get_user
from .game_utils import has_game_expired
from ... import database


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

    board = load_from_pgn(game.pgn)
    turn = "White" if board.turn else "Black"
    expired = has_game_expired(game)  # TODO: make games actually expire
    game_over = (
        game.winner is not None or expired or board.is_game_over()
    )  # TODO: add claim_draw

    status = (
        f"__Game ID: {game.id}__\n"
        f"{white_mention} (White) **VS.** {black_mention} (Black)\n"
    )
    if not game_over:
        status += (
            f"*{turn}'s turn.*\n\n"
            f"This game will expire on {game.expiration_date},\nresulting in {turn} losing, if they don't make a move."
        )
    else:
        try:
            reason = get_game_over_reason(board)  # TODO: add claim_draw
        except RuntimeError as err:
            if expired:
                reason = "Game expired."
            elif game.winner == database.WHITE:
                reason = "Black conceded."
            elif game.winner == database.BLACK:
                reason = "White conceded."
            elif game.winner == database.DRAW:
                reason = "Opponents have agreed to draw."
            else:
                logger.error("Failed to get the reason for the game over")
                raise err

        if game.winner == database.WHITE:
            result = f"White wins - {reason}."
        elif game.winner == database.BLACK:
            result = f"Black wins - {reason}."
        elif game.winner == database.DRAW:
            result = f"Draw - {reason}."
        else:
            logger.error(f"Game winner is None in game #{game.id}")
            try:
                result = f"{get_winner(board)} - {reason}."  # TODO: add claim_draw
            except RuntimeError as err:
                logger.error("Failed to get the result for a finished game")
                raise err

        status += f"\n**Game over!** {result}"

    return status, to_png(board)

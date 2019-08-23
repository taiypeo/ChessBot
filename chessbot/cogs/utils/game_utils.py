from .chess_utils import load_from_pgn, get_winner, get_game_over_reason, get_turn
from ... import constants, database
from ...config import EXPIRATION_TIMEDELTA

from loguru import logger
import datetime


def get_game(user_id: int, game_id: int) -> database.Game:
    if game_id is None:
        user = (
            database.session.query(database.User).filter_by(discord_id=user_id).first()
        )
        if user is None:
            raise RuntimeError(f"User #{user_id} does not exist in the database")

        game = user.last_game
        if game is None:
            raise RuntimeError(f"User #{user_id} does not have a last game")
    else:
        game = database.session.query(database.Game).get(game_id)
        if game is None:
            raise RuntimeError(f"Game #{game_id} does not exist in the database")

    return game


def has_game_expired(game: database.Game) -> bool:
    if game.expiration_date is not None:
        return datetime.datetime.now() > game.expiration_date
    return False  # game finished before expiring


def update_game(game: database.Game, recalculate_expiration_date: bool = False) -> None:
    if game.winner is not None:
        return  # if the game has already finished, there is nothing to do

    board = load_from_pgn(game.pgn)
    turn = get_turn(board)

    if has_game_expired(game):
        game.win_reason = "Game expired"
        if turn == constants.WHITE:
            game.winner = constants.BLACK
        else:
            game.winner = constants.WHITE

        database.add_to_database(game)

        return

    if recalculate_expiration_date:
        game.expiration_date = datetime.datetime.now() + EXPIRATION_TIMEDELTA
        database.add_to_database(game)

    claim_draw = game.draw_proposed
    both_agreed = game.white_accepted_draw and game.black_accepted_draw

    try:
        winner = get_winner(board, claim_draw=claim_draw, both_agreed=both_agreed)
        reason = get_game_over_reason(
            board, claim_draw=claim_draw, both_agreed=both_agreed
        )
    except RuntimeError as err:
        logger.info("The game has not ended yet:")
        logger.info(
            err
        )  # not actually an error, just the reasoning behind the game not being over

        return

    game.winner = winner
    game.win_reason = reason
    game.expiration_date = None
    database.add_to_database(game)


def who_offered_draw(game: database.Game) -> int:
    if not game.draw_proposed or not (
        game.white_accepted_draw or game.black_accepted_draw
    ):
        raise RuntimeError("Nobody offered to draw")

    if game.white_accepted_draw:
        return constants.WHITE
    else:
        return constants.BLACK

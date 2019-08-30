from .chess_utils import (
    load_from_pgn,
    get_winner,
    get_game_over_reason,
    get_turn,
    undo,
    save_to_pgn,
)
from .user_utils import get_database_user
from .elo_utils import recalculate_elo
from ... import constants, database
from ...config import EXPIRATION_TIMEDELTA

from loguru import logger
import datetime


def get_game(user_id: int, game_id: int) -> database.Game:
    if game_id is None:
        user = get_database_user(user_id)
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


def update_game(
    game: database.Game,
    recalculate_expiration_date: bool = False,
    reset_action: bool = False,
    concede_side: int = None,
    only_check_expiration: bool = False,
) -> None:
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

        recalculate_elo(game)
        return

    if only_check_expiration:
        return

    if concede_side in [constants.WHITE, constants.BLACK]:
        if concede_side == constants.WHITE:
            game.winner = constants.BLACK
        else:
            game.winner = constants.WHITE

        concede_side_str = constants.turn_to_str(concede_side).capitalize()
        game.win_reason = f"{concede_side_str} conceded"
        game.expiration_date = None

        database.add_to_database(game)

        recalculate_elo(game)
        return

    if recalculate_expiration_date:
        game.expiration_date = datetime.datetime.now() + EXPIRATION_TIMEDELTA
        database.add_to_database(game)

    claim_draw = game.action_proposed == constants.ACTION_DRAW
    undo_last = game.action_proposed == constants.ACTION_UNDO
    both_agreed = game.white_accepted_action and game.black_accepted_action

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

        if undo_last and both_agreed:
            undo(board)
            game.pgn = save_to_pgn(board)
            database.add_to_database(game)

        if reset_action:
            game.action_proposed = constants.ACTION_NONE
            game.white_accepted_action = False
            game.black_accepted_action = False

            database.add_to_database(game)

        return

    game.winner = winner
    game.win_reason = reason
    game.expiration_date = None
    database.add_to_database(game)

    recalculate_elo(game)


def update_ongoing_games() -> None:
    games = (
        database.session.query(database.Game)
        .filter(database.Game.winner.is_(None))
        .all()
    )
    for game in games:
        update_game(game, only_check_expiration=True)
        # checking only the expiration, since after each meaningful action (!offer, !move, etc.)
        # the game is updated automatically


def who_offered_action(game: database.Game) -> int:
    if game.action_proposed == constants.ACTION_NONE or not (
        game.white_accepted_action or game.black_accepted_action
    ):
        raise RuntimeError("Nobody offered an action")

    if game.white_accepted_action:
        return constants.WHITE
    else:
        return constants.BLACK


def is_player(game: database.Game, user: database.User) -> bool:
    return user in [game.white, game.black]


def which_player(game: database.Game, user: database.User) -> int:
    if user == game.white:
        return constants.WHITE
    elif user == game.black:
        return constants.BLACK
    else:
        raise RuntimeError(
            f"User #{user.discord_id} is not a player in game #{game.id}"
        )

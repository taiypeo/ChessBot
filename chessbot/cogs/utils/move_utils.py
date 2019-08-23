from .chess_utils import load_from_pgn, save_to_pgn, move, get_turn
from ... import database, constants


def handle_turn_check(user: database.User, game: database.Game) -> None:
    board = load_from_pgn(game.pgn)

    if (get_turn(board) == constants.WHITE and user == game.black) or (
        get_turn(board) == constants.BLACK and user == game.white
    ):
        raise RuntimeError(
            f"User #{user.id} tried to move on the wrong turn in game #{game.id}"
        )


def handle_move(game: database.Game, san_move: str) -> None:
    board = load_from_pgn(game.pgn)

    try:
        move(board, san_move)
    except ValueError as err:
        raise err

    game.pgn = save_to_pgn(board)
    database.add_to_database(game)

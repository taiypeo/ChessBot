from .game_utils import update_game
from ... import database


def handle_draw_accept(user: database.User, game: database.Game) -> None:
    if (game.white_accepted_draw and game.white == user) or (
        game.black_accepted_draw and game.black == user
    ):
        raise RuntimeError("Can't accept your own draw offer")
    elif game.white == user:
        game.white_accepted_draw = True
    elif game.black == user:
        game.black_accepted_draw = True

    update_game(game)

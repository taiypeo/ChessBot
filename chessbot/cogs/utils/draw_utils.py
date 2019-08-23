from .game_utils import which_player
from ... import database, constants


def handle_draw_offer(user: database.User, game: database.Game) -> None:
    try:
        player = which_player(game, user)
    except RuntimeError as err:
        raise err

    if player == constants.WHITE:
        game.white_accepted_draw, game.black_accepted_draw = True, False
    else:
        game.white_accepted_draw, game.black_accepted_draw = False, True

    game.draw_proposed = True
    database.add_to_database(game)

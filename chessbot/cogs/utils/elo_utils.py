from ... import database, constants


def recalculate_elo(game: database.Game) -> None:
    if game is None:
        raise RuntimeError("Game is None")

    white = game.white
    black = game.black
    game_result = game.winner

    if game_result is None:
        raise RuntimeError("Game is not over yet")
    if white is None or black is None:
        raise RuntimeError("Either white or black is None")
    if white.elo is None or black.elo is None:
        raise RuntimeError("Either white or black does not have an elo rating")

    WEa = round(1 / (1 + 10 ** ((black.elo - white.elo) / 400)), 2)
    white_actual = constants.result_to_int(game_result)

    white_delta = white_actual - WEa

    white_diff = white_delta * constants.ELO_K
    black_diff = (-white_delta) * constants.ELO_K

    white.elo += white_diff
    black.elo += black_diff

    if white.elo < 0:
        white.elo = 0
    if black.elo < 0:
        black.elo = 0

    database.add_to_database(white)
    database.add_to_database(black)

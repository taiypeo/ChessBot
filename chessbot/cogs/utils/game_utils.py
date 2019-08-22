from ... import database
import datetime


def get_game(user_id: int, game_id: int) -> database.Game:
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
    else:
        raise RuntimeError(f"No game found for {user_id}")


def has_game_expired(game: database.Game) -> bool:
    return datetime.datetime.now() > game.expiration_date

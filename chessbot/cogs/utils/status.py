from discord import File, Member
from discord.ext import commands

from .chess_functions import load_from_pgn, to_png
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

    return None


def get_game_status(game: database.Game) -> str:
    pass

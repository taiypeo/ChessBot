import chess
import chess.pgn
import chess.svg

import discord

import io
from cairosvg import svg2png
from loguru import logger


def load_from_pgn(pgn_str: str) -> chess.Board:
    game = chess.pgn.read_game(io.StringIO(pgn_str))  # TODO: maybe add a PGN check?
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)

    return board


def save_to_pgn(board: chess.Board) -> str:
    game = chess.pgn.Game.from_board(board)
    exporter = chess.pgn.StringExporter(headers=False, variations=False, comments=False)
    return game.accept(exporter)


def move(board: chess.Board, san_move: str) -> None:
    try:
        move = board.parse_san(san_move)
    except ValueError as err:
        logger.error(f"Invalid SAN move: {san_move}")
        raise err

    board.push(move)


def to_png(board: chess.Board, size: int = 400) -> discord.File:
    try:
        svg_image = chess.svg.board(board, lastmove=board.peek(), size=size)
    except IndexError:
        svg_image = chess.svg.board(board, size=size)

    png = svg2png(bytestring=svg_image.encode("UTF-8"))
    return discord.File(io.BytesIO(png), filename="board.png")


def get_winner(board: chess.Board, claim_draw: bool = False) -> str:
    winner = board.result(claim_draw=claim_draw)
    if winner == "1-0":
        return "White wins."
    elif winner == "0-1":
        return "Black wins."
    elif winner == "1/2-1/2":
        return "Draw."
    else:
        raise RuntimeError("Game is not over yet, can't get the winner")

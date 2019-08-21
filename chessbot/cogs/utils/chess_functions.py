import chess
import chess.pgn
import chess.svg

import io
from cairosvg import svg2png
from loguru import logger


def load_from_pgn(pgn_str: str) -> chess.Board:
    game = chess.pgn.read_game(io.StringIO(pgn_str))
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
    except ValueError:
        logger.error(f"Invalid SAN move: {san_move}")
        raise ValueError

    board.push(move)


def to_svg(board: chess.Board, size: int = 400) -> io.BytesIO:
    try:
        svg_image = chess.svg.board(board, lastmove=board.peek(), size=size)
    except IndexError:
        svg_image = chess.svg.board(board, size=size)

    png = svg2png(bytestring=svg_image.encode('UTF-8'))
    return io.BytesIO(png)

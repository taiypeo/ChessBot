import chess
import chess.pgn
import chess.svg

import discord

import io
from cairosvg import svg2png
from loguru import logger

from ... import constants


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


def undo(board: chess.Board) -> None:
    try:
        board.pop()
    except IndexError:
        logger.error("Can't undo the last move")


def to_png(board: chess.Board, size: int = 400) -> discord.File:
    args = {"size": size}

    try:
        lastmove = board.peek()
        args["lastmove"] = lastmove

        if board.is_check():
            args["check"] = board.king(board.turn)
    except IndexError:
        logger.info("No last move in this board, skipping")
        pass

    svg_image = chess.svg.board(board, **args)

    png = svg2png(bytestring=svg_image.encode("UTF-8"))
    return discord.File(io.BytesIO(png), filename="board.png")


def get_winner(
    board: chess.Board, claim_draw: bool = False, both_agreed: bool = False
) -> int:
    if claim_draw and both_agreed:
        return constants.DRAW

    winner = board.result(claim_draw=claim_draw)
    if winner == "1-0":
        return constants.WHITE
    elif winner == "0-1":
        return constants.BLACK
    elif winner == "1/2-1/2":
        return constants.DRAW
    else:
        raise RuntimeError("Game is not over yet, can't get the winner")


def get_game_over_reason(
    board: chess.Board, claim_draw: bool = False, both_agreed: bool = False
) -> str:
    if claim_draw and both_agreed:
        return "Both opponents agreed to a draw"

    reasons = [
        "Checkmate",
        "Stalemate",
        "Insufficient material",
        "Draw by the seventyfive-move rule",
        "Draw by the fivefold repetition rule",
    ]
    checks = [
        board.is_checkmate(),
        board.is_stalemate(),
        board.is_insufficient_material(),
        board.is_seventyfive_moves(),
        board.is_fivefold_repetition(),
    ]

    if claim_draw:
        reasons = [
            *reasons,
            *["Draw by the fifty-move rule", "Draw by the threefold repetition rule"],
        ]
        checks = [
            *checks,
            *[board.can_claim_fifty_moves(), board.can_claim_threefold_repetition()],
        ]

    possible = [reason for reason, check in zip(reasons, checks) if check]
    if len(possible) > 0:
        return possible[0]
    else:
        raise RuntimeError("No possible game over reason")


def get_turn(board: chess.Board) -> int:
    return constants.WHITE if board.turn else constants.BLACK

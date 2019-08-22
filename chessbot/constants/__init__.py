WHITE = 0
BLACK = 1
DRAW = 2


def turn_to_str(turn: int) -> str:
    if turn < 0 or turn > DRAW:
        raise RuntimeError("Invalid turn in turn_to_str()")

    return ["white", "black", "draw"][turn]

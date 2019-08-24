WHITE = 0
BLACK = 1
DRAW = 2


def turn_to_str(turn: int) -> str:
    if turn < 0 or turn > DRAW:
        raise RuntimeError("Invalid turn in turn_to_str()")

    return ["white", "black", "draw"][turn]


def result_to_int(result: int) -> int:
    if result < 0 or result > DRAW:
        raise RuntimeError("Invalid result in result_to_int()")

    if result == WHITE:
        return 1  # 1-0
    elif result == BLACK:
        return 0  # 0-1
    else:
        return 0.5  # 1/2 - 1/2


ACTION_NONE = 0
ACTION_DRAW = 1
ACTION_UNDO = 2

OFFERABLE_ACTIONS = {"DRAW": ACTION_DRAW, "UNDO": ACTION_UNDO}

# kind of a hack but I'm too tired to think of anything better
OFFERABLE_ACTIONS_REVERSE = {ACTION_DRAW: "DRAW", ACTION_UNDO: "UNDO"}

ELO_K = 24

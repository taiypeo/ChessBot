WHITE = 0
BLACK = 1
DRAW = 2


def turn_to_str(turn: int) -> str:
    if turn < 0 or turn > DRAW:
        raise RuntimeError("Invalid turn in turn_to_str()")

    return ["white", "black", "draw"][turn]


ACTION_NONE = 0
ACTION_DRAW = 1
ACTION_BACK = 2

OFFERABLE_ACTIONS = {"DRAW": ACTION_DRAW, "BACK": ACTION_BACK}

# kind of a hack but I'm too tired to think of anything better
OFFERABLE_ACTIONS_REVERSE = {ACTION_DRAW: "DRAW", ACTION_BACK: "BACK"}

from gameState import Directions


def direction_to_elec_move(dir: Directions) -> str:
    if dir == Directions.UP:
        return "N"
    elif dir == Directions.LEFT:
        return "W"
    elif dir == Directions.DOWN:
        return "S"
    elif dir == Directions.RIGHT:
        return "E"
    elif dir == Directions.NONE:
        return "X"

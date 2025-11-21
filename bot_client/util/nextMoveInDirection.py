from gameState import Location, Directions


def next_move_in_direction(
    current_location: Location, direction: Directions
) -> Location:
    row, col = current_location.row, current_location.col
    new_location = Location(None)

    if direction == Directions.UP:
        col += 1
    elif direction == Directions.DOWN:
        col -= 1
    elif direction == Directions.LEFT:
        row -= 1
    elif direction == Directions.RIGHT:
        row += 1

    new_location.update((row << 8) | col)

    return new_location

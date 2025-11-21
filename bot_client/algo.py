from gameState import Location


# Define a class to represent nodes in the grid
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start node to current node
        self.h = 0  # Heuristic cost (estimated cost to reach goal)
        self.f = 0  # Total cost: g + h

    # heap sorting based on 'f' values
    def __lt__(self, other):
        return self.f < other.f

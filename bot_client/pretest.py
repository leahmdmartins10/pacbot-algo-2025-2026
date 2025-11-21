import pickle

# Load the precomputed distances
with open("maze_distances.pkl", "rb") as f:
    distances = pickle.load(f)

def get_distance(start, goal):
    # Returns None if goal is unreachable.
    return distances.get(start, {}).get(goal)

# Example usage:
start_cell = (11, 13)  # For example, a free cell
goal_cell = (5, 16)  # Example goal cell

dist = get_distance(start_cell, goal_cell)
if dist is not None:
    print(f"Shortest distance from {start_cell} to {goal_cell} is: {dist}")
else:
    print(f"Cell {goal_cell} is unreachable from {start_cell}.")

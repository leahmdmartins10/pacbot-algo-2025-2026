import pickle
from collections import deque

# Maze wall representation (each integer is one row).
wallArr = [                           #27
    0b0000_1111111111111111111111111111,  # row 0
    0b0000_1000000000000110000000000001,  # row 1
    0b0000_1011110111110110111110111101,  # row 2
    0b0000_1011110111110110111110111101,  # row 3
    0b0000_1011110111110110111110111101,  # row 4
    0b0000_1000000000000000000000000001,  # row 5
    0b0000_1011110110111111110110111101,  # row 6
    0b0000_1011110110111111110110111101,  # row 7
    0b0000_1000000110000110000110000001,  # row 8
    0b0000_1111110111110110111110111111,  # row 9
    0b0000_1111110111110110111110111111,  # row 10
    0b0000_1111110110000000000110111111,  # row 11
    0b0000_1111110110111111110110111111,  # row 12
    0b0000_1111110110111111110110111111,  # row 13
    0b0000_1111110000111111110000111111,  # row 14
    0b0000_1111110110111111110110111111,  # row 15
    0b0000_1111110110111111110110111111,  # row 16
    0b0000_1111110110000000000110111111,  # row 17
    0b0000_1111110110111111110110111111,  # row 18
    0b0000_1111110110111111110110111111,  # row 19
    0b0000_1000000000000110000000000001,  # row 20
    0b0000_1011110111110110111110111101,  # row 21
    0b0000_1011110111110110111110111101,  # row 22
    0b0000_1000110000000000000000110001,  # row 23
    0b0000_1110110110111111110110110111,  # row 24
    0b0000_1110110110111111110110110111,  # row 25
    0b0000_1000000110000110000110000001,  # row 26
    0b0000_1011111111110110111111111101,  # row 27
    0b0000_1011111111110110111111111101,  # row 28
    0b0000_1000000000000000000000000001,  # row 29
    0b0000_1111111111111111111111111111   # row 30
]

rows = len(wallArr)
cols = 28  # Updated number of columns

# Create grid: True indicates a free (walkable) cell; False indicates a wall.
grid = []
for row_val in wallArr:
    # Convert the integer to a binary string, padded to 28 bits.
    row_bits = bin(row_val)[2:].zfill(cols)
    # '0' means open cell and '1' means wall.
    grid.append([bit == '0' for bit in row_bits])

# Collect all free cells and create an optional index mapping.
free_cells = []
cell_index = {}
for r in range(rows):
    for c in range(cols):
        if grid[r][c]:
            cell_index[(r, c)] = len(free_cells)
            free_cells.append((r, c))

# Build neighbors list for each free cell (four cardinal directions).
neighbors = {}
for (r, c) in free_cells:
    adjacent = []
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc]:
            adjacent.append((nr, nc))
    neighbors[(r, c)] = adjacent

# Precompute distances using BFS for each free cell.
# distances[cell_A] is a dictionary mapping cell_B to the shortest distance.
distances = {}
for start in free_cells:
    dist_map = {start: 0}
    queue = deque([start])
    
    while queue:
        current = queue.popleft()
        for nbr in neighbors[current]:
            if nbr not in dist_map:
                dist_map[nbr] = dist_map[current] + 1
                queue.append(nbr)
    distances[start] = dist_map

# Save the computed distances to a file for later fast lookup.
with open("maze_distances.pkl", "wb") as f:
    pickle.dump(distances, f)

print("Precomputation complete and saved to maze_distances.pkl")

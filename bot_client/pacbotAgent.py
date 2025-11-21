from gameState import *
from gameState import Directions
from gameState import reversedDirections
from copy import deepcopy
import random

DIRECTION_VECTORS = {
    Directions.UP: (-1, 0),
    Directions.LEFT: (0, -1),
    Directions.DOWN: (1, 0),
    Directions.RIGHT: (0, 1),
}

class PacbotAgent:

    def __init__(self, state):
        self.state: GameState = state
        self.tmp_state: GameState = state
        self.lastMove = None

    def dangerCost(self, row, col) -> int:
        nonFrightenedGhosts = [ghost for ghost in self.tmp_state.ghosts if not ghost.isFrightened()]

        for ghost in nonFrightenedGhosts:
            distance = self.manhattanDistance(ghost.location.row, ghost.location.col, row, col)
            if distance < 5:
                return 100
            elif distance < 15:
                return 50
            elif distance < 25:
                return 25
            elif distance < 35:
                return 10
        return 0

    direction = [Directions.RIGHT, Directions.UP, Directions.LEFT, Directions.DOWN]
    counter = 0

    def manhattanDistance(self, row1, col1, row2, col2):
        return abs(row1 - row2) + abs(col1 - col2)

    def degreeAt(self, row, col) -> int:
        deg = 0
        for dirVector in DIRECTION_VECTORS.values():
            nr = row + dirVector[0]
            nc = col + dirVector[1]
            if not self.tmp_state.wallAt(nr, nc):
                deg += 1
        return deg

    def corridorEntranceAndLen(self, row, col, max_len=100):
        if self.degreeAt(row, col) > 2:
            return (row, col, 0)

        prev = None
        cur = (row, col)
        length = 0
        steps = 0
        while steps < max_len:
            deg = self.degreeAt(cur[0], cur[1])
            # If we found a junction or an isolated cell, stop
            if deg > 2 or deg == 0:
                return (cur[0], cur[1], length)

            # Find the next neighbour that isn't the previous cell
            next_cells = []
            for v in DIRECTION_VECTORS.values():
                nr = cur[0] + v[0]
                nc = cur[1] + v[1]
                if not self.tmp_state.wallAt(nr, nc) and (prev is None or (nr, nc) != prev):
                    next_cells.append((nr, nc))

            if not next_cells:
                return (cur[0], cur[1], length)

            # Continue down the corridor (there should usually be exactly one choice)
            prev = cur
            cur = next_cells[0]
            length += 1
            steps += 1

        # Max length reached; return current spot
        return (cur[0], cur[1], length)

    def legalDirections(self):
        legal = []
        for dirName, dirVector in DIRECTION_VECTORS.items():
            newRow = self.tmp_state.pacmanLoc.row + dirVector[0]
            newCol = self.tmp_state.pacmanLoc.col + dirVector[1]
            if not self.tmp_state.wallAt(newRow, newCol):
                legal.append(dirName)
        return legal
    
    def findSafePathToPellet(self, startRow, startCol):
        """
        Find a reasonably safe path to some pellet, using a
        risk-aware Dijkstra-style search.

        Returns a list of Directions (like before) or None.
        """

        import heapq

        start = (startRow, startCol)

        # Priority queue items: (cost_so_far, row, col, path_as_dirs)
        open_heap: list[tuple[float, int, int, list[Directions]]] = []
        heapq.heappush(open_heap, (0.0, startRow, startCol, []))

        # Best known cost to reach each cell
        best_cost: dict[tuple[int, int], float] = {start: 0.0}

        bestPath: list[Directions] | None = None
        bestScore: float = float("inf")

        while open_heap:
            cost, row, col, path = heapq.heappop(open_heap)
            pos = (row, col)

            # If we already found a cheaper way to this cell, skip this entry
            if cost > best_cost.get(pos, float("inf")):
                continue

            # --- Goal check: current cell has a pellet ---
            if self.tmp_state.PelletAt(row, col):
                # corridor / dead-end analysis at this pellet
                entranceRow, entranceCol, corridor_len = self.corridorEntranceAndLen(
                    row, col
                )

                dead_end_penalty = 0
                if corridor_len > 0:
                    # Pacman steps from entrance into the corridor
                    pac_to_entrance = max(0, len(path) - corridor_len)

                    nonFrightened = [
                        g for g in self.tmp_state.ghosts if not g.isFrightened()
                    ]
                    ghost_to_entrance = float("inf")
                    for ghost in nonFrightened:
                        gd = self.manhattanDistance(
                            ghost.location.row,
                            ghost.location.col,
                            entranceRow,
                            entranceCol,
                        )
                        ghost_to_entrance = min(ghost_to_entrance, gd)

                    # If the ghost can contest the entrance, treat it as very risky
                    if ghost_to_entrance - pac_to_entrance < 3:
                        dead_end_penalty = 1000

                # total score for this pellet path:
                #   path cost so far + big penalty if it's a scary dead-end
                score = cost + dead_end_penalty

                if score < bestScore:
                    bestScore = score
                    bestPath = path
                # Keep going; there might be an even better pellet elsewhere
                # (we're not doing a single-target A*, but multi-target search)
                # so we don't "return" here.
                # continue

            # --- Expand neighbors ---

            for dirName, dirVector in DIRECTION_VECTORS.items():
                newRow = row + dirVector[0]
                newCol = col + dirVector[1]
                newPos = (newRow, newCol)

                # Must be walkable
                if self.tmp_state.wallAt(newRow, newCol):
                    continue

                # Base danger at this tile
                tileDanger = self.dangerCost(newRow, newCol)

                # Hard prune VERY dangerous tiles
                if tileDanger >= 50:
                    continue

                # Step cost: distance + weighted danger
                # (tune 0.3 up or down to make Pacbot more or less risk-averse)
                step_cost = 1.0 + 0.3 * tileDanger

                new_cost = cost + step_cost

                # Only keep this neighbour if we found a cheaper path to it
                if new_cost < best_cost.get(newPos, float("inf")):
                    best_cost[newPos] = new_cost
                    heapq.heappush(
                        open_heap,
                        (new_cost, newRow, newCol, path + [dirName]),
                    )

        return bestPath
    # this will be similar to findSafePathToPellet but instead of pellets,
    # it's going to search for a path to the fruit
    def findPathToFruit(self, startRow, startCol, fruitRow, fruitCol):
        from collections import deque
        visited = set()
        queue = deque([(startRow, startCol, [])])
        bestPath = None


    def act(self):
        if self.state.gameMode == GameModes.PAUSED:
            return

        decompressGameState(self.tmp_state, compressGameState(self.state))

        pacManRow, pacManCol = self.tmp_state.pacmanLoc.row, self.tmp_state.pacmanLoc.col
        ghosts = self.tmp_state.ghosts

        closestGhost = min(ghosts, key=lambda g: self.manhattanDistance(g.location.row, g.location.col, pacManRow, pacManCol))
        ghostDistance = self.manhattanDistance(closestGhost.location.row, closestGhost.location.col, pacManRow, pacManCol)
        closestGhostFrightened = closestGhost.isFrightened()

        legalMoves = self.legalDirections()

        if closestGhostFrightened:
            if ghostDistance <= 3:
                vectorToGhost = (closestGhost.location.row - pacManRow, closestGhost.location.col - pacManCol)
                bestDir = None
                bestDot = float('-inf')

                for dirName, dirVector in DIRECTION_VECTORS.items():
                    if dirName in legalMoves:
                        dot = dirVector[0] * vectorToGhost[0] + dirVector[1] * vectorToGhost[1]
                        if dot > bestDot:
                            bestDot = dot
                            bestDir = dirName

                self.state.queueAction(numTicks=4, pacmanDir=bestDir)
                self.lastMove = bestDir
                return
            elif ghostDistance <= 10:
                # check distance between ghost and nearest pellet
                minPelletDistance = float('inf')
                for pellet in self.tmp_state.pellets[:]: # prevent modifying a list while iterating over it
                    pelletDistance = self.manhattanDistance(pacManRow, pacManCol, pellet.row, pellet.col)
                    if pelletDistance < minPelletDistance:
                        minPelletDistance = pelletDistance  
                
                if ghostDistance < minPelletDistance:
                    vectorToGhost = (closestGhost.location.row - pacManRow, closestGhost.location.col - pacManCol)
                    bestDir = None
                    bestDot = float('-inf')

                    for dirName, dirVector in DIRECTION_VECTORS.items():
                        if dirName in legalMoves:
                            dot = dirVector[0] * vectorToGhost[0] + dirVector[1] * vectorToGhost[1]
                            if dot > bestDot:
                                bestDot = dot
                                bestDir = dirName

                    self.state.queueAction(numTicks=4, pacmanDir=bestDir)
                    self.lastMove = bestDir
                    return
                else:
                    # seek pellets, closer to the pellet than the ghost
                    pathToPellet = self.findSafePathToPellet(pacManRow, pacManCol)
                    if pathToPellet and len(pathToPellet) > 0:
                        nextMove = pathToPellet[0]
                        self.state.queueAction(numTicks=4, pacmanDir=nextMove)
                        self.lastMove = nextMove
                        return 
            else:
                # seek pellets
                pathToPellet = self.findSafePathToPellet(pacManRow, pacManCol)
                if pathToPellet and len(pathToPellet) > 0:
                    nextMove = pathToPellet[0]
                    self.state.queueAction(numTicks=4, pacmanDir=nextMove)
                    self.lastMove = nextMove
                    return

        # Ghost is NOT frightened — play defensively
        dangerCosts = {}
        safeMoves = []
        for move in legalMoves:
            delta = DIRECTION_VECTORS[move]
            nextRow = pacManRow + delta[0]
            nextCol = pacManCol + delta[1]

            # Base danger from ghosts
            danger = self.dangerCost(nextRow, nextCol)

            # Small noise to break ties randomly
            danger += random.uniform(0, 0.5)

            # Penalize going back the way we came
            if move == reversedDirections.get(self.lastMove):
                danger += 30

            # Simulate the move
            simState = deepcopy(self.tmp_state)
            if simState.simulateAction(numTicks=4, pacmanDir=move):
                dangerCosts[move] = danger
                safeMoves.append(move)

        if safeMoves:
            bestMove = min(safeMoves, key=lambda move: dangerCosts[move])
        else:
            # No simulated move is safe, fallback to least dangerous legal move
            bestMove = min(legalMoves, key=lambda move: self.dangerCost(
                pacManRow + DIRECTION_VECTORS[move][0],
                pacManCol + DIRECTION_VECTORS[move][1]
            ))

        self.state.queueAction(numTicks=4, pacmanDir=bestMove)
        self.lastMove = bestMove
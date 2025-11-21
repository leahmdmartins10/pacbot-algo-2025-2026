from gameState import Location, GameState

GRID_WIDTH = 27
GRID_HEIGHT = 31


class Cluster:
    def __init__(self, x: int, y: int, n: int) -> None:
        self.x = x
        self.y = y
        self.location = Location(None)
        self.location.update((x << 8) | y)
        self.num_clusters = n
        self.magnitude = 0
        self.x_swings, self.y_swings = int(GRID_WIDTH / self.num_clusters), int(
            GRID_HEIGHT / self.num_clusters
        )
        self.x_swings += 1
        self.y_swings -= 1


    def update_magnitude(self, gs: GameState) -> None:
        """
        Original behavior: for every pellet in the fixed window around
        the cluster center, add 100/(d²) if gs.pacmanLoc is not at the cluster center,
        or 100 if it is.
        """
        self.magnitude = 0.0
        # Use the fixed window around the cluster center.
        start_row = self.location.row - self.x_swings
        end_row = self.location.row + self.x_swings
        start_col = self.location.col - self.y_swings
        end_col = self.location.col + self.y_swings
        # Compute the distance from the (global) Pacman location to the cluster center.
        d = abs(gs.pacmanLoc.row - self.location.row) + abs(gs.pacmanLoc.col - self.location.col)
        # gs.pacmanLoc.distance_to(self.location)
        factor = 100 / (d**2) if d != 0 else 100

        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                if gs.pelletAt(i, j):
                    self.magnitude += factor

    def center_location(self) -> Location:
        """
        Return the cluster center location (constant).
        """
        return self.location
        
        
        # for i in range(
        #     self.location.row - self.x_swings,
        #     self.location.row + self.x_swings,
        # ):
        #     for j in range(
        #         self.location.col - self.y_swings,
        #         self.location.col + self.y_swings,
        #     ):
        #         if gs.pelletAt(i, j):
        #             if (x := gs.pacmanLoc.distance_to(self.location)) != 0:
        #                 self.magnitude += 100 / (x**2)
        #             else:
        #                 self.magnitude += 100

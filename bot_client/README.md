
This folder contains _sample_ Python code to function as a high-level client for the Pacbot competition.

Teams are encouraged (and expected) to modify client code to fit their navigation algorithms and robot communication protocols.

To run the sample bot client, simply run `python pacbotClient.py`.

Other useful files:

-   `decisionModule.py`: a sample decision module (policy) with an asynchronous loop and game state locking capabilities
-   `gameState.py`: a game state object which parses serialized data and offers simple methods to interact with and predict the game state
-   `walls.py`: a binary representation of the maze walls (identical to `initWalls` in the server code)



# Pacbot Decision Module
## Overview
The `decisionModule` selects a target using `target.py` based on the current game state, then applies the A* search algorithm for pathfinding, guided by heuristic functions from `heuristic.py`

## Implementation Details
The `TargetSelector` class determines the best target location based on:
- **Game stage:** Early-game prioritizes pellet clearing, while end-game prioritizes fruit collection.
- **Ghost behavior:** If a ghost is frightened, Pacbot attempts to chase it.
- **Super pellets:** If a normal ghost is too close, Pacbot may prioritize eating a super pellet.

The `Heuristic` class computes movement costs using multiple factors:
- **Distance to target** (Manhattan distance)
- **Avoiding proximity to normal ghosts**
- **Chasing frightened ghosts** (if safe to do so)
- **Cluster-based incentives** (preferring movement within high-pellet-density regions)



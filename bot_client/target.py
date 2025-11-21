from typing import List, Tuple
from gameState import GameState, Location, GameModes, Ghost
import traceback

DISTANCE_THRESHOLD = 5
AVAILABLE = 1
UNAVAILABLE = 0
EATEN = -1

FRUIT_ROW = 17
FRUIT_COL = 13


SUPER_PELLET_POSITIONS: List[Tuple[int, int]] = [(3, 1), (3, 26), (23, 1), (23, 26)]


class TargetSelector:
    def __init__(self, state: GameState) -> None:
        """
        Construct a new decision module object
        """
        self.state = state
        # Game state object to store the game information
        self.location = None

        self.init_super_pellets()

    def init_super_pellets(self) -> List[Location]:
        self.super_pellets: List[Location] = []
        for iterator in SUPER_PELLET_POSITIONS:
            loc = Location(self.state)
            loc.row = iterator[0]
            loc.col = iterator[1] 
            self.super_pellets.append(loc)
            
    def get_closest_super_pellet_by_ghosts(self) -> Location:
            """
            Returns the available super pellet (Location) for which
            the average distance (using Manhattan distance) to all normal ghosts
            is smallest.
            """
            # Gather available super pellet locations.
            available_super = list(self.get_available_super_pellets())
            if not available_super:
                return None

            # Get normal ghosts (those not frightened).
            normal_ghosts = list(self.get_normal_ghosts())
            if not normal_ghosts:
                # Fall back to the nearest super pellet from Pacman's perspective, e.g.
                return min(available_super, key=lambda sp: self.state.pacmanLoc.distance_to(sp))

            def avg_distance_to_normal_ghosts(sp) -> float:
                total = 0
                for g in normal_ghosts:
                    total += sp.distance_to(g.location) #abs(sp.row - g.location.row) + abs(sp.col - g.location.col)
                return total / len(normal_ghosts)

            # Choose the super pellet with the smallest average distance to all normal ghosts.
            chosen = min(available_super, key=avg_distance_to_normal_ghosts)
            # print(chosen.row, chosen.col)
            return chosen
    

       


    def decide_target_location(self) -> Location:
        """
        Decide the target location for the pacman
        """
        try:
            idx = None
            for i, cl in enumerate(self.state.clusters):
                if self.state.point_in_cluster(
                    (self.state.pacmanLoc.row, self.state.pacmanLoc.col), cl):
                    idx = i
                    break
            self.state.current_cluster_index = idx
                
            num_pellets = self.state.numPellets() - len(list(self.get_available_super_pellets()))
            frightened_ghosts = list(self.get_frightened_ghosts())
            normal_ghosts = list(self.get_normal_ghosts())
            
            if (
                num_pellets == 1 and 
                (list(self.get_available_super_pellets()) or 
                len(frightened_ghosts) >= 2 )
                ):  
                self.state.blockPellets = True
            else:
                self.state.blockPellets = False        
            # if fruit is not available, for first stage sweep pellets
            # if num_pellets > 210 or num_pellets < 25:
            #     return None
            # if fruit is available: go for it - add is_fruit_av? -> if distance to it is less than fright steps.

            # any other scenario, deal normally as you would.
            # else:
                                # check if there is a frightened ghost.
                
                
                
            if(normal_ghosts):
                ghosts_in_cluster = [
                    ghost for ghost in normal_ghosts
                    if self.state.current_cluster_index is not None and 
                    self.state.point_in_cluster((ghost.location.row, ghost.location.col), self.state.clusters[self.state.current_cluster_index])
                ]
                closest_ghost = self.get_closest_ghost(normal_ghosts)

                # Condition: If two or more ghosts are in the cluster, trigger superpellet mode.
                if len(ghosts_in_cluster) >= 3:
                    if self.state.gameMode == GameModes.CHASE and list(self.get_available_super_pellets()):
                        # self.state.blockPellets = False
                        self.state.blockSuper = False
                        return self.get_closest_super_pellet()
                
                elif(self.state.gameMode == GameModes.CHASE and closest_ghost.location.distance_to(self.state.pacmanLoc) < 3):
                    closest_super = self.get_closest_super_pellet()
                    if(closest_super is not None and self.state.pacmanLoc.distance_to(closest_super)<3):
                        # self.state.blockPellets = False
                        self.state.blockSuper = False
                        return closest_super
            if (
                self.isFruitAvailable()
                and self.state.pacmanLoc.distance_to(self.state.fruitLoc)
                <= self.state.fruitSteps
            ):
                loc = self.state.fruitLoc
                safe = all(loc.distance_to(self.state.pacmanLoc) < loc.distance_to(g.location) - 3 or 
                           loc.distance_to(g.location) > 5 or
                           g.location.distance_to(self.state.pacmanLoc) < g.location.distance_to(loc) 
                            for g in normal_ghosts)
                if(safe):
                    self.state.blockSuper = True
                    # self.state.blockPellets = False
                    return self.state.fruitLoc
            # frightened_ghosts = list(self.get_frightened_ghosts())
            if (frightened_ghosts):
                self.state.blockSuper = True
                # self.state.blockPellets = False
                closest_ghost = self.get_closest_ghost(frightened_ghosts)
                # print("Closest ghost:", closest_ghost.color)
                if (
                    self.state.pacmanLoc.distance_to(closest_ghost.location)
                    <= closest_ghost.frightSteps * 0.8
                ):
                    #return None
                    return closest_ghost.location
            # except ValueError as v:
            #     print(f"Error in finding closest ghost: {v}")
            # else:
                #aim for super pellets
                # normal_ghosts = list(filter(lambda g: not g.isFrightened(), self.state.ghosts)) 
                

                    

            
            if self.state.gameMode == GameModes.CHASE and self.state.current_cluster_index is not None:
                superpellets = [superpellet for superpellet in list(self.get_available_super_pellets()) if self.state.point_in_cluster((superpellet.row, superpellet.col), self.state.clusters[idx])]
                r0, r1 = self.state.clusters[idx]["row_range"]
                c0, c1 = self.state.clusters[idx]["col_range"]
                
                cluster_pellets = [
                    (x, y) for x in range(r0, r1+1) for y in range(c0, c1+1) 
                    if self.state.pelletAt(x, y) and self.state.point_in_cluster((x, y), self.state.clusters[idx])
                    and (x, y) not in SUPER_PELLET_POSITIONS
                ]
                if(not cluster_pellets and superpellets):
                    # self.state.blockPellets = False
                    self.state.blockSuper = False
                    return superpellets[0]
            if num_pellets < 5 and list(self.get_available_super_pellets()):  
                    # self.state.blockPellets = True
                    self.state.blockSuper = False
                    # print("i m here")
                    return self.get_closest_super_pellet_by_ghosts()
                
            if num_pellets == 0 and list(self.get_available_super_pellets()):  
                    # self.state.blockPellets = False
                    self.state.blockSuper = False
                    return self.get_closest_super_pellet_by_ghosts()    
            
            # elif self.state.gameMode == GameModes.SCATTER:
            # else:
            self.state.blockPellets = False
            self.state.blockSuper = True
            return None
                
                        
                        
                    # if self.state.gameMode == GameModes.CHASE:                
                    #     normal_ghosts = list(self.get_normal_ghosts())
                    #     if(normal_ghosts):
                    #         closest_ghost = self.get_closest_ghost(normal_ghosts)
                    #         if closest_ghost.location.distance_to(self.state.pacmanLoc) < 6:
                    #             return self.get_closest_super_pellet()
                    #     else:
                    #         return None
                    # elif self.state.gameMode == GameModes.SCATTER:
                    #     return None
                # except Exception as e:
                #     print(f"Except-all: {e}")
                    # return None

        except Exception as e:
            print(f"Error in deciding target location: {e}")
            traceback.print_exc()
            return None

    def get_frightened_ghosts(self):
        """
        Get the frightened ghosts in the game
        """
        return filter(lambda g: g.isFrightened() and not g.spawning and not g.eaten, self.state.ghosts)

    def get_normal_ghosts(self):
        """
        Get the normal ghosts in the game
        """
        return filter(lambda g: not g.isFrightened() and (not g.spawning or g.trappedSteps < 4) and not g.eaten, self.state.ghosts)

    def isFruitAvailable(self) -> bool:
        """
        Check if the fruit is available in the game
        """

        return self.state.fruitAt(FRUIT_ROW, FRUIT_COL)

    def get_available_super_pellets(self):
        """
        Get the available super pellets in the game
        """
        return filter(
            lambda sp: self.state.pelletAt(sp.row, sp.col), self.super_pellets
        )

    def get_closest_super_pellet(self) -> Location:
        """
        Get the closest super pellet to the current location of Pacman
        """
        try:

            available_super_pellets = list(self.get_available_super_pellets())
            if(available_super_pellets):
                closest_super_pellet = min(
                    available_super_pellets,
                    key=lambda point: self.state.pacmanLoc.distance_to(point),
                )

                return closest_super_pellet
            else:
                return None

        except Exception as e:
            print(f"Error in _find_closest_super_pellet: {e}")
            traceback.print_exc()
            return None

    def get_closest_ghost(self, ghosts) -> Ghost:
        """
        Get the closest frightened ghost to the current location of Pacman
        """

        return min(
            ghosts, key=lambda ghost: self.state.pacmanLoc.distance_to(ghost.location)
        )


# need this function for reference.
# def get_furthest_super_pellet(self) -> Location:
#     """
#     Get the closest super pellet to the current location of Pacman
#     """
#     try:

#         available_super_pellets = self.get_available_super_pellets()
#         furthest_super_pellet = max(
#             available_super_pellets,
#             key=lambda point: self.state.pacmanLoc.distance_to(point),
#         )
#         return furthest_super_pellet

#     except Exception as e:
#         print(f"Error in _find_furthest_super_pellet: {e}")
#         return None

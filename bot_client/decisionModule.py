import asyncio
import heapq
from typing import List, Tuple
from algo import Node
from heuristic import Heuristic
from target import TargetSelector
from util import location_to_direction, direction_to_elec_move, next_move_in_direction
from gameState import GameState, Directions, Location, GameModes
import sys
import time

import traceback

import websockets
from websockets.exceptions import ConnectionClosedError  # type: ignore

# from pacbotAgent import *

measure_time_enabled = "-measure-time" in sys.argv
shouldRunElec = "-elec" in sys.argv
showPrintStatements = "-debug" in sys.argv


DISTANCE_THRESHOLD = 8

ALL_DIRECTIONS = [
    Directions.UP,
    Directions.DOWN,
    Directions.LEFT,
    Directions.RIGHT,
]

SUPER_PELLET_POSITIONS: list[tuple[int, int]] = [(3, 1), (3, 26), (23, 1), (23, 26)]


class DecisionModule:
    """
    Sample implementation of a decision module for high-level
    programming for Pacbot, using asyncio.
    """

    def __init__(self, state: GameState) -> None:
        """
        Construct a new decision module object
        """

        # Game state object to store the game information
        self.state = state
        self.heuristic = Heuristic(state)
        self.target = TargetSelector(state)
        self.previous_location = self.state.pacmanLoc
        
        self.state.blockSuper = True
        self.state.blockPellets = False
        
        self.same_move_counter = 0
        self.hc_move: Directions | None = None

        self.next_queued_action = None
        self.last_queued_action = None
        self.sent = False
        
        # self.agent = PacbotAgent(self.state)

    async def create_server(self):
        print("serving")
        self.pi_server = await websockets.serve(self.pi_handle, "0.0.0.0", 3005)

    async def pi_handle(self, conn):
        while True:
            """
            print(self.last_queued_action, self.next_queued_action, self.sent)
            if self.last_queued_action != self.next_queued_action and not self.sent:
                await conn.send(self.next_queued_action)
                self.sent = True
            """
            if self.next_queued_action is not None:
                await conn.send(self.next_queued_action)
                print("sent ", self.next_queued_action)
            await asyncio.sleep(0)

    # TODO: Consider chase vs scatter mode.
    def _get_target(self) -> Location:

        try:
            self.target.location = self.target.decide_target_location()
            # if None - go for the closest pellet.
            if self.target.location is None or (not self.state.ready and not self._is_pellet_safe(
                self.target.location)
            ):
                if self.state.numPellets() == 1:
                    self.state.blockPellets = False
                
                if(self.state.gameMode == GameModes.CHASE):
                    self.target.location = self.find_closest_cluster_pellet() 
                
                if(self.target.location is None or self.state.gameMode == GameModes.SCATTER):
                    self.target.location = self._find_closest_safe_pellet()

            return self.target.location

        except Exception as e:
            print(f"error in get target: {e}")
            traceback.print_exc()
            return self._get_away_from_ghosts_when_cant_find_pellets()

    def _is_pellet_safe(self, pellet: Location) -> bool:
        if type(pellet) is not Location:
            pelletLoc = Location(self.state)
            pelletLoc.update((pellet[0] << 8) | pellet[1])
            pellet = pelletLoc
        distanceThreshold = DISTANCE_THRESHOLD
        if(self.state.gameMode== GameModes.SCATTER):
            distanceThreshold = DISTANCE_THRESHOLD
            
            
        normal_ghosts = self.target.get_normal_ghosts() #[g for g in self.state.ghosts if (not g.isFrightened() and not g.spawning)]
        return all(
            pellet.distance_to(self.state.pacmanLoc) < pellet.distance_to(g.location) - 5 or
            pellet.distance_to(g.location) > distanceThreshold or
            g.location.distance_to(self.state.pacmanLoc) < g.location.distance_to(pellet) -3
            for g in normal_ghosts
        )

    def are_pellets_in_core(self) -> bool:
        return any(
            self.state.pelletAt(x, y) for x in range(5, 23) for y in range(5, 23)
        )
    def find_closest_cluster_pellet(self) -> Location | None:
        idx = self.state.current_cluster_index
        if idx is None:
            return None
        
        r0, r1 = self.state.clusters[idx]["row_range"]
        c0, c1 = self.state.clusters[idx]["col_range"]

        # all pellets in this cluster
        all_in_cluster = [
            (x,y)
            for x in range(r0, r1+1)
            for y in range(c0, c1+1)
            if self.state.pelletAt(x,y)
            and self.state.point_in_cluster((x,y), self.state.clusters[idx])
        ]

        if not all_in_cluster:
            return None

        # dead‑ends for this cluster
        deadends = self.state.deadends_by_cluster[idx]

        # is the super‑pellet for this cluster still present?
        super_r, super_c = SUPER_PELLET_POSITIONS[idx]
        super_still_there = self.state.superPelletAt(super_r, super_c)

        # filter out dead‑ends if super is still there
        if super_still_there:
            candidates = [p for p in all_in_cluster if p not in deadends]
        else:
            candidates = all_in_cluster

        # if filtering removed everything, allow deadends back in
        if not candidates:
            candidates = all_in_cluster

        # now pick the closest safe pellet among candidates
        safe = [
            p for p in candidates
            if self._is_pellet_safe((p[0], p[1]))
            and (p not in SUPER_PELLET_POSITIONS)  # still block supers here
        ]
        if not safe:
            return None

        # choose by distance (or include any heuristics)
        x,y = min(safe, key=lambda p: self.state.pacmanLoc.distance_to_overload(p))
        pellet = Location(self.state)
        pellet.row, pellet.col = x, y
        return pellet
    
    # def find_closest_cluster_pellet(self):
    #     """
    #     Determines the next pellet target using a cluster-based approach.
    #     """          
    #     cluster_safe_pellets = [
    #         (x, y)
    #         for x in range(0, 32)
    #         for y in range(0, 29)
    #         if self.state.pelletAt(x, y) and self.state.point_in_cluster((x, y), self.state.current_cluster)
    #         and self._is_pellet_safe((x, y))
    #         and (x, y) not in SUPER_PELLET_POSITIONS
    #     ]

    #     if(cluster_safe_pellets):
    #         closest_pellet = min(cluster_safe_pellets,
    #             key=lambda pellet: self.state.pacmanLoc.distance_to_overload(pellet))
            
    #         pelletLoc = Location(self.state)
    #         pelletLoc.row, pelletLoc.col = closest_pellet[0], closest_pellet[1]
    #         return pelletLoc

    #     return None
        # # If there are pellets in the current cluster, select the closest one (using Manhattan distance).
        # ###########need to be safe
        
        # distanceThreshold = DISTANCE_THRESHOLD
        # if(self.state.gameMode== GameModes.SCATTER):
        #     distanceThreshold = 3
            
            
        #     return all(
        #         pellet.distance_to(g.location) > )
        
        
        # if current_cluster_pellets:

        #     return closest_pellet

        # # If the current cluster is empty, search for the next densest cluster.
        # cluster_pellet_counts = []
        # for cl in clusters:
        #     if cl == current_cluster:
        #         continue
        #     pellets_in_cluster = [
        #         pellet for pellet in self.state.pellets
        #         if not pellet.is_super and self.point_in_cluster((pellet.row, pellet.col), cl)
        #     ]
        #     cluster_pellet_counts.append((cl, len(pellets_in_cluster), pellets_in_cluster))

        # # If none of the other clusters have any pellets, return None.
        # if not cluster_pellet_counts:
        #     return None

        # # Select the cluster with the highest number of pellets.
        # densest_cluster, _, pellets_in_densest = max(cluster_pellet_counts, key=lambda x: x[1])

        # # Return the closest pellet in the densest cluster.
        
        # ####need to be safe
        
        
        # if pellets_in_densest:
        #     closest_pellet = min(
        #         pellets_in_densest,
        #         key=lambda pellet: abs(curr.row - pellet.row) + abs(curr.col - pellet.col)
        #     )
        #     return closest_pellet
        
        # else #fall back

        # return None
    

    def _find_closest_safe_pellet(self) -> Location:
        """
        Find the closest pellet to the current location of Pacman
        It skips any pellets that are within a CONSTANT distance of any normal ghost

        If no pellets are found, it tries to run away from all ghosts
        """
        low, high_x, high_y = 1, 29, 26        
        # if (
        #     self.state.gameMode == GameModes.SCATTER
        #     and self.are_pellets_in_core() is True
        # ):
        #     low = 5
        #     high_x = 23
        #     high_y = 23

        safe_pellets = [
            (x, y)
            for x in range(low, high_x + 1)
            for y in range(low, high_y + 1)
            if self.state.pelletAt(x, y)
            and self._is_pellet_safe((x, y))
            and (x, y) not in SUPER_PELLET_POSITIONS
        ]
        
        filtered = []
        for pellet in safe_pellets:
            x, y = pellet
            # find the cluster this pellet sits in
            for idx, cl in enumerate(self.state.clusters):
                r0, r1 = cl["row_range"]
                c0, c1 = cl["col_range"]
                if r0 <= x <= r1 and c0 <= y <= c1:
                    break
            else:
                idx = None

            # if it’s in a cluster whose super‑pellet is still up, drop dead‑ends
            if idx is not None:
                # super pellet coords for this cluster
                sr, sc = SUPER_PELLET_POSITIONS[idx]
                if self.state.superPelletAt(sr, sc):
                    if (x, y) in self.state.deadends_by_cluster[idx]:
                        # skip this pellet—it’s a known dead‑end
                        continue

            filtered.append(pellet)

        # 3) if filtering removed everything, fall back to the original list
        if filtered:
            safe_pellets = filtered

        try:
            if not safe_pellets:
                return self._get_away_from_ghosts_when_cant_find_pellets()
                
            x, y = min(
                safe_pellets,
                key=lambda point: self.state.pacmanLoc.distance_to_overload(point)
                - self.heuristic._cluster_heuristic(point),
            )
            closest_safe_pellet = Location(self.state)
            closest_safe_pellet.row, closest_safe_pellet.col = x, y
            # .update((x << 8) | y)
            return closest_safe_pellet

        except Exception as e:
            traceback.print_exc()
            print(f"Error in _find_closest_safe_pellet: {e}")
            
            return self._get_away_from_ghosts_when_cant_find_pellets()

    def _get_away_from_ghosts_when_cant_find_pellets(self):
        # print("No pellets found, running away from ghosts")
        try:
            # ghost_plans = [
            #     next_move_in_direction(g.location, g.guessPlan())
            #     for g in self.state.ghosts
            # ]
            ghost_plans = []
            for g in self.state.ghosts:
                g.guessPlan()  # sets g.plannedDirection internally
                if g.plannedDirection is not None and not g.isFrightened:
                    ghost_plans.append(next_move_in_direction(g.location, g.plannedDirection))


            all_possible_moves = map(
                lambda d: next_move_in_direction(self.state.pacmanLoc, d),
                ALL_DIRECTIONS,
            )
            # Remove any moves that hit a wall or a ghost is planning to move to
            valid_moves = list(filter(
                lambda loc: not self.state.wallAt(loc.row, loc.col)
                and loc not in ghost_plans,
                all_possible_moves,
            ))

            # If there are no possible moves, stay in the current location
            if not valid_moves:
                return self.state.pacmanLoc

            normal_ghosts = list(self.target.get_normal_ghosts()) #[g for g in self.state.ghosts if not g.isFrightened() and not g.spawning]
            if normal_ghosts and ghost_plans:
                best_move = max(
                    valid_moves,
                    key=lambda move: min(
                        move.distance_to(planned_loc) for planned_loc in ghost_plans
                        #move.distance_to(g.location) for g in normal_ghosts
                    ),
                )

                return best_move
            return self.state.pacmanLoc
        except Exception as e:
            traceback.print_exc()
            print(f"Error in _get_away_from_ghosts_when_cant_find_pellets: {e}")
            return self.state.pacmanLoc

    def _get_next_move(self) -> Directions:
        target_location = self._get_target()
        # need to insert the target logic here.

        start = self.state.pacmanLoc
        path = self._algo(start, target_location)
        if path is not None and len(path) > 0:
            _move = path[0]
            move = location_to_direction(start, _move)
            return move

        fallback = self._get_away_from_ghosts_when_cant_find_pellets()
        return location_to_direction(start, fallback)
        # return Directions.NONE


    def _algo(self, start, target):
        start = (start.row, start.col)
        target = (target.row, target.col)
        if self.state.wallAt(target[0], target[1]):
            print("target at wall debug")
        
        ##wait for ghost        
        if self.state.superPelletAt(target[0], target[1]):
            manhattan = abs(start[0] - target[0]) + abs(start[1] - target[1])
            if manhattan <= 1:
                normal_ghosts = list(filter(lambda g: not g.isFrightened() and not g.spawning, self.state.ghosts))
                if(normal_ghosts):
                    closest_ghost = self.target.get_closest_ghost(normal_ghosts)
                    if closest_ghost.location.distance_to(self.state.pacmanLoc) < 3:
                        self.state.blockSuper = False
                        self.state.ready = False
                        return [target]
                    else:
                        self.state.ready = True
                        return []  # No movement; we are already beside the target.

        open_list: list[Node] = list()
        closed_set = set()
        head = Node(start, None)
        head.g = 0
        head.h = self.heuristic.get_overall_heuristic(start, target)
        head.f = head.h
        normal_ghosts = list(self.target.get_normal_ghosts())
        heapq.heappush(open_list, head)

        while open_list:
            curr = heapq.heappop(open_list)
            if curr.position == target:
                path: list[tuple[int, int]] = []
                while curr.position != start:
                    try:
                        path.append(curr.position)
                        curr = curr.parent
                    except Exception as e:
                        traceback.print_exc()
                        print(f"Error in _algo: {e}")
                        break
                path.reverse()
                return path

            closed_set.add((curr.position[0], curr.position[1]))
            all_neighbors = map(
                lambda dir: (curr.position[0] + dir[0], curr.position[1] + dir[1]),
                [(1, 0), (-1, 0), (0, 1), (0, -1)],
            )

            valid_neighbors = filter(
                lambda pos: not self.state.wallAt(pos[0], pos[1]),
                all_neighbors,
            )
            
            for neighbor in valid_neighbors:
                if (neighbor[0], neighbor[1]) in closed_set:
                    continue
                if self.state.blockSuper and self.state.superPelletAt(neighbor[0], neighbor[1]):
                    # print("h")
                    continue
                if self.state.blockPellets and self.state.pelletAt(neighbor[0], neighbor[1]) and not self.state.superPelletAt(neighbor[0], neighbor[1]):
                    continue
                if any(ghost.location.distance_to_overload(neighbor) == 0 for ghost in normal_ghosts):
                    continue
                #if ghost skip
                
                node = Node(neighbor, curr)
                node.g = curr.g + 1
                node.h = self.heuristic.get_overall_heuristic(neighbor, target)
                node.f = node.g + node.h
                heapq.heappush(open_list, node)
        print("target:",target, "start", start )
        print("No path found")
        return None
    
    async def decisionLoop(self) -> None:
        left_count = 5
        right_count = 5
        stationary_count = 0
        STATIONARY_MAX_T = 1.0
        prev_loc = None
        # end_time = 0
        while self.state.isConnected():
            if self.state.gameMode == GameModes.PAUSED.value:
                # print("paused")
                await asyncio.sleep(0.01)  # change if pacman isn't moving as expected
                continue
            
            # if len(self.state.writeServerBuf):
			# 	await asyncio.sleep(0)
			# 	continue
            
            self.state.lock()
            # start_time = time.time() 
            # print(end_time-start_time)
            for cluster in self.heuristic._clusters:
                cluster.update_magnitude(self.state)
            # Act with the given agent
			# self.agent.act()

            self.hc_move = None
            if self.state.currLives == 3 and left_count > 0:
                left_count -= 1
                self.hc_move = Directions.LEFT
            elif self.state.currLives == 2 and right_count > 0:
                right_count -= 1
                self.hc_move = Directions.RIGHT

            if measure_time_enabled:
                start_time = time.time()  # Start timer

            if self.previous_location == self.state.pacmanLoc:
                self.same_move_counter += 1

            else:
                self.same_move_counter = 0
                self.previous_location = self.state.pacmanLoc


            if measure_time_enabled:
                end_time = time.time()  # End timer
                with open("time_log.txt", "a") as file:
                    file.write(f"{end_time-start_time}\n")
            # for cluster in self.heuristic._clusters:
            #     cluster.update_magnitude(self.state)
            
            next_move = (
                self.hc_move if self.hc_move is not None else self._get_next_move()
            )

            if shouldRunElec:
                self.state.queueAction(1, next_move)
                next_move = direction_to_elec_move(next_move)
                self.last_queued_action = self.next_queued_action
                self.next_queued_action = next_move
                self.sent = False
            else:
                self.state.queueAction(1, next_move)

            self.state.unlock()
            await asyncio.sleep(0.03)

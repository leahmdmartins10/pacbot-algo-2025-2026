from gameState import GameState, Location, get_distance
from cluster import Cluster

DISTANCE_THRESHOLD = 5

# This probably belongs in a constants file
NUM_CLUSTERS = 4
CLUSTER_STARTING_COORDINATES = [[7, 8], [7, 20], [20, 8], [20, 20]]


class Heuristic:
    def __init__(self, state: GameState):
        self.state = state
        self.heuristics = [
            self._manhattan_distance,
            self._avoid_too_close_to_normal_ghosts,
            self._prefer_close_to_scared_ghosts,
            self._cluster_heuristic,
        ]
        self.num_heuristics = len(self.heuristics)

        self._clusters = [
            Cluster(coords[0], coords[1], 4) for coords in CLUSTER_STARTING_COORDINATES
        ]

    def _m_distance(self, curr, other):
        return abs(curr[0] - other[0]) + abs(curr[1] - other[1])
        
    def _manhattan_distance(self):
        return get_distance(self.curr, self.target)
        #return abs(self.curr[0] - self.target[0]) + abs(self.curr[1] - self.target[1])
    #self.curr.distance_to(self.target)

    def _avoid_too_close_to_normal_ghosts(self):
        """
        Avoid being too close to normal ghosts
        """
        normal_ghosts = list(filter(lambda g: not g.isFrightened() and (not g.spawning or g.trappedSteps < 4), self.state.ghosts))

        if not normal_ghosts:
            return 0
            
        penalties = map(
            lambda g: DISTANCE_THRESHOLD
            - min(DISTANCE_THRESHOLD, g.location.distance_to_overload(self.curr)) , 
            normal_ghosts,
        )
        #self._m_distance(self.curr, (g.location.row, g.location.col)))
        return sum(penalties)

    def _prefer_close_to_scared_ghosts(self):
        """
        Prefers being close to scared ghosts
        """

        scared_ghosts = list(filter(lambda g: g.isFrightened() and not g.spawning, self.state.ghosts))

        if not scared_ghosts:
            return 0

        bonuses = map(
            lambda g: min(DISTANCE_THRESHOLD, g.location.distance_to_overload(self.curr))#self._m_distance(self.curr, (g.location.row, g.location.col)))
            - DISTANCE_THRESHOLD,
            scared_ghosts,
        )

        return sum(bonuses) 
    
    def _cluster_heuristic(self, curr: Location, target: Location = None) -> float:
        #return 0
        """
        Improved cluster heuristic that mimics the original behavior:
        - Clusters are updated (using Pacman’s global location) once per decision cycle.
        - For each cluster, if the candidate location is inside the cluster's window,
            then the full magnitude is used; otherwise, the value decays with distance.
        """
        best_discount = 0.0
        for cluster in self._clusters:
            center = cluster.center_location()
            # Compute Manhattan distance between candidate position and cluster center.
            d = abs(curr[0] - center.row) + abs(curr[1] - center.col)
            window_size = cluster.x_swings + cluster.y_swings
            if d < window_size:
                discount = cluster.magnitude
            else:
                # Decay the discount as candidate gets farther from cluster center.
                discount = cluster.magnitude / (d + 1)
            if discount > best_discount:
                best_discount = discount
        return best_discount

    

    # def _cluster_heuristic(self, curr):
    #     return 0
        # # Bring all clusters up to date wrt current pacman location
        # for cluster in self._clusters:
        #     cluster.update_magnitude(self.state)

        # # idea: select what cluster region the pellet belongs to, then return the magnitude of that cluster.
        # # This is used as a 'discount' of the distance, to incentivise staying in cluster region
        # try:
        #     x_s, y_s = self._clusters[0].x_swings, self._clusters[0].y_swings
        # except Exception as e:
        #     print(f"Error in swings: {e}")
        #     print(curr)
        #     return 0

        # n_x, n_y = curr[0], curr[1]

        # cluster_num = -1

        # for i in range(len(self._clusters)):
        #     # idea: start in cluster region 1. If both elements of diffs negative, pellet in cluster region. If not check another region, until found
        #     c_x, c_y = (
        #         self._clusters[i].location.row + x_s,
        #         self._clusters[i].location.col + y_s,
        #     )
        #     diffs = n_x - c_x, n_y - c_y
        #     if diffs[0] < 0 and diffs[1] < 0:
        #         cluster_num = i
        #         break

        # if cluster_num == -1:
        #     # something went wrong, dont apply heuristic
        #     return 0
        # return self._clusters[cluster_num].magnitude

    ###########take pellets into considetation
    
    # def get_overall_heuristic(self, curr: Location, target: Location):
    #     self.curr = curr
    #     self.target = target
        
    #     if(self.state.pelletAt(curr.row, curr.col)):
            

    #     best_heuristic_score = float("-inf")  # Initialize with negative infinity

    #     for h in self.heuristics:
    #         heuristic_score = 0

    #         if h == self._cluster_heuristic:
    #             continue
    #             curr_int = [curr[0], curr[1]]
    #             heuristic_score = h(curr_int)

    #         elif h in [
    #             self._avoid_too_close_to_normal_ghosts,
    #             self._prefer_close_to_scared_ghosts,
    #         ]:
    #             heuristic_score = h() * 1000  # Experiment with weights

    #         else:
    #             heuristic_score = h()

    #         heuristic_score /= self.num_heuristics
    #         best_heuristic_score = max(best_heuristic_score, heuristic_score)

    #     return best_heuristic_score

    def get_overall_heuristic(self, curr: Location, target: Location):
        """
        Computes a weighted sum of the individual heuristic scores.
        tune the weight of each heuristic by adjusting the variables below.
        """
        # Set the current and target for functions that rely on them.
        self.curr = curr
        self.target = target

        # Tunable weights for each heuristic
        manhattan_weight = 1.0
        avoid_normal_weight = 1000.0
        prefer_scared_weight = 1000.0
        cluster_weight = 0 #1.0

        # Compute each heuristic individually.
        h_manhattan = self._manhattan_distance() * manhattan_weight
        h_avoid_normal = self._avoid_too_close_to_normal_ghosts() * avoid_normal_weight
        h_prefer_scared = self._prefer_close_to_scared_ghosts() * prefer_scared_weight
        # h_cluster = self._cluster_heuristic(curr, target) * cluster_weight
        h_pellet = -int(self.state.pelletAt(curr[0], curr[1]))
        # print(h_avoid_normal)
        # print("s", h_prefer_scared)
        # Sum them up for the overall heuristic.
        overall_heuristic = h_manhattan + h_avoid_normal + h_prefer_scared  + h_pellet #+ h_cluster
        # print(overall_heuristic)
        return overall_heuristic
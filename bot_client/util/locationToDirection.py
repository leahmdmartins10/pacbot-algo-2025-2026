from typing import Optional
from gameState import Location, Directions


def location_to_direction(p, n) -> Directions:
    p = (p.row, p.col)
    try:
        if(p[0]==n[0] and p[1]==n[1]):
            return Directions.NONE
        
        if p[0] == n[0]:
            if p[1] < n[1]:
                return Directions.RIGHT
            else:
                return Directions.LEFT
        else:
            if p[0] < n[0]:
                return Directions.DOWN
            else:
                return Directions.UP
    except:
        return Directions.NONE

# def location_to_direction(p: Location, n: Location) -> Directions:
#     try:
#         if p.row == n.row:
#             if p.col < n.col:
#                 return Directions.RIGHT
#             else:
#                 return Directions.LEFT
#         else:
#             if p.row < n.row:
#                 return Directions.DOWN
#             else:
#                 return Directions.UP
#     except:
#         return Directions.NONE
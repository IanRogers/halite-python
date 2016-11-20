from hlt import *
from networking import *

myID, gameMap = getInit()
sendInit("Nomad")

def move(location):
    site = gameMap.getSite(location)
    if site.strength < site.production:
        return Move(location, STILL)
    neighbour_not_me = False
    for d in CARDINALS:
        neighbour_site = gameMap.getSite(location, d)
        if neighbour_site.owner != myID:
            neighbour_not_me = True
            if neighbour_site.strength < site.strength:
                return Move(location, d)
    if neighbour_not_me:
        return Move(location, STILL)
    if site.strength >= site.production * 5:
        max_strength = 0;
        go = STILL;
        for d in CARDINALS:
            neighbour_site = gameMap.getSite(location, d)
            if neighbour_site.owner == myID:
                if neighbour_site.strength > max_strength:
                    go = d;
        return Move(location, go)
    return Move(location, STILL)
   


while True:
    moves = []
    gameMap = getFrame()
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                moves.append(move(location))
    sendFrame(moves)

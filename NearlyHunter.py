from hlt import *
from networking import *

myID, gameMap = getInit()
width = gameMap.width
height = gameMap.height
enemy = Location(0, 0)
sendInit("Hunter")

def heading(me, them, wrap):
    diff = them - me
    dist = abs(diff)
    return diff if dist < (wrap/2) else -diff

def move(location):
    site = gameMap.getSite(location)

    if site.strength < site.production:
        # just been born
        return Move(location, STILL)

    # try to kill an enemy
    neighbour_not_me = False
    enemy_neighbour = False
    for d in CARDINALS:
        neighbour_site = gameMap.getSite(location, d)
        if neighbour_site.owner != myID:
            neighbour_not_me = True
            if neighbour_site.owner != 0:
                enemy_neighbour = True
                if neighbour_site.strength < site.strength:
                    return Move(location, d)
    # can't kill, so resist an enemy
    if enemy_neighbour:
        return Move(location, STILL)
 
    if neighbour_not_me:
        # pick highest production blank we can conquer
        max_production = 0
        go = STILL
        for d in CARDINALS:
            neighbour_site = gameMap.getSite(location, d)
            if neighbour_site.owner == 0:
                if neighbour_site.strength < site.strength:
                    if neighbour_site.production > max_production:
                        max_production = neighbour_site.production
                        go = d
        return Move(location, go)
 
    # go hunting if we can
    if site.strength >= site.production * 5:
        xm = heading(location.x, enemy.x, width)
        if xm != 0:
            go = WEST if xm < 0 else EAST
            if gameMap.getSite(location, go).owner == myID:
                return Move(location, go)
        ym = heading(location.y, enemy.y, height)
        if ym != 0:
            go = NORTH if ym < 0 else SOUTH
            if gameMap.getSite(location, go).owner == myID:
                return Move(location, go)

    # just chill dude, you're still growing
    return Move(location, STILL)
   


while True:
    moves = []
    gameMap = getFrame()
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            who = gameMap.getSite(location).owner
            if who == myID:
                moves.append(move(location))
            elif who != 0:
                enemy = location
    sendFrame(moves)

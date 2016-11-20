from hlt import *
from networking import *

myID, gameMap = getInit()
width = gameMap.width
width2 = width // 2
height = gameMap.height
height2 = height // 2
max_size = max(width, height) // 1.5

sendInit("Virus")


def highest_production(me, tiles):
    # pick highest production tile we can conquer and we're not already attacking, or stay still to resist
    max_production = 0
    go = STILL
    strength = me.strength
    for who in tiles:
        them = who[0]
        if them.strength < strength and them.location not in attacking:
            if them.production > max_production:
                max_production = them.production
                go = who[1]
    return go


def nearest_straight_edge(location, heading, lives):
    if location in edge_runs:
        return edge_runs[location][0]
    if location in straight_runs:
        return straight_runs[location]
    if lives < 0:
        return max_size
    if gameMap.getSite(location).owner != myID:
        return -1

    dist = 1 + nearest_straight_edge(gameMap.getLocation(location, heading), heading, lives - 1)
    if dist < max_size:
        straight_runs[location] = dist
    return dist

# edges have a distance 0
def nearest_edge(location):
    if location in edge_runs:
        return edge_runs[location]

    go = WEST
    closest = max_size
    tup = (closest, go)

    for d in CARDINALS:
        c = 1 + nearest_straight_edge(gameMap.getLocation(location, d), d, closest)
        if c < closest:
            closest = c
            tup = (closest, d)

    # now we have the real value
    edge_runs[location] = tup
    return tup

# returns (absdist, delta)
def away1d(me, them, max):
    dist = them - me;
    adist = abs(dist)
    return (adist, dist) if adist < max else (adist, -dist)

# location to location, away from the longest centre. (0, 0) is top-left
def away(me, them):
    tx = away1d(me.x, them.x, width2)
    ty = away1d(me.y, them.y, height2)
    if tx[0] > ty[0]:
        return EAST if tx[1] > 0 else WEST
    else:
        return SOUTH if ty[1] > 0 else NORTH

def move(location):
    site = gameMap.getSite(location)

    blank = []
    enemy = []
    me = []
    me_d = []
    for d in CARDINALS:
        loc = gameMap.getLocation(location, d)
        them = loc.site
        who = (them, d)
        owner = them.owner
        if owner == 0:
            blank.append(who)
        elif owner == myID:
            me.append(who)
            me_d.append(d)
        else:
            enemy.append(who)

    if len(enemy) > 0:
        # be agressive if we can, or defend
        edge_runs[location] = (0, STILL)
        return highest_production(site, enemy)

    if len(blank) > 0:
        # take something if we can, or maybe move elsewhere
        edge_runs[location] = (0, STILL)
        go = highest_production(site, blank)
        if go != STILL:
            return go

    if site.strength < site.production * 5:
        # just chill dude, you're still growing
        return STILL

    if len(me) == 4:
        # in the middle of a sea of me
        # move to nearest edge
        return nearest_edge(location)[1]

    if len(me) == 2:
        if count == 2:
            # special case for game start
            return me_d[0]
        if NORTH in me_d and SOUTH in me_d:
            # north-south corridor   
            return me[0][1] if me[0][0].strength > me[1][0].strength else me[1][1]
        if EAST in me_d and WEST in me_d:
            # east-west corridor   
            return me[0][1] if me[0][0].strength > me[1][0].strength else me[1][1]

    # corner or flat edge, stay still
    return STILL



while True:
    moves = []
    edge_runs = {}
    straight_runs = {}
    attacking = {}
    count = 0
    gameMap = getFrame()
    for y in range(height):
        for x in range(width):
            site = gameMap.fetchSite(x, y)
            if site.owner == myID:
                location = site.location
                count += 1
                go = move(location)
                if go != STILL and location not in attacking:
                    attacking[location] = True
                    moves.append(Move(location, go))
    sendFrame(moves)

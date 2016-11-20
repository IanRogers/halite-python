from hlt import *
from networking import *

myID, gameMap = getInit()
width = gameMap.width
width2 = width // 2
height = gameMap.height
height2 = height // 2
max_wrap = max(width2, height2)
WRAPS = [(NORTH, height2), (EAST, width2), (SOUTH, height2), (WEST, width2)]

centre_loc = Location(width2, height2)
edge = []
for y in range(0, height):
    row = []
    for x in range(0, width):
        row.append(False)
    edge.append(row)
edge_runs = {}

sendInit("Virus")


def highest_production(me, tiles):
    # pick highest production tile we can conquer or stay still to resist
    max_production = 0
    go = STILL
    strength = me.strength
    for who in tiles:
        them = who[0]
        if them.strength <= strength:
            if them.production > max_production:
                max_production = them.production
                go = who[1]
    return go


def nearest_straight_edge(location, heading, lives):
    if lives < 0 or gameMap.getSite(location).owner != myID:
        return (-1, STILL)
    if location in edge_runs:
        return edge_runs[location]

    go = (1 + nearest_straight_edge(gameMap.getLocation(location, heading), heading, lives - 1), heading)
    edge_runs[location] = go
    return go

# edges have a distance 0
def nearest_edge(location):
    if location in edge_runs:
        return edge_runs[location]

    go = NORTH # will be overwritten
    closest = max_wrap
    edge_runs[location] = (closest, go) # temp entry while we figure it out

    for (d, w) in WRAPS:
        c = nearest_straight_edge(location, d, w)
        if c < closest:
            closest = c
            go = d

    # now we have the real value
    tup = (closest, go)
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
        them = gameMap.getSite(location, d)
        who = (them, d)
        owner = them.owner
        if owner == 0:
            blank.append(who)
        elif owner == myID:
            me.append(who)
            me_d.append(d)
        else:
            enemy.append(who)

    edge[location.x][location.y] = False

    if len(enemy) > 0:
        # be agressive if we can, or defend
        edge[location.x][location.y] = True
        edge_runs[location] = (0, STILL)
        return highest_production(site, enemy)

    if len(blank) > 0:
        # take something if we can, or maybe move elsewhere
        edge[location.x][location.y] = True
        edge_runs[location] = (0, STILL)
        go = highest_production(site, blank)
        if go != STILL:
            return go

    if site.strength < site.production * 5:
        # just chill dude, you're still growing
        return STILL

    if len(me) == 1 or len(me) == 3:
        # we're in a dead end or flat edge, stay there
        return STILL

    if len(me) == 2:
        if NORTH in me_d and SOUTH in me_d:
            # north-south corridor   
            return away(centre_loc, location)
        if EAST in me_d and WEST in me_d:
            # east-west corridor   
            return away(centre_loc, location)
        # corner, stay still
        return STILL

    # in the middle of a sea of me
    # move to nearest edge
    return nearest_edge(location)[1]


while True:
    moves = []
    edge_runs = {}
    tot_x = 0;
    tot_y = 0;
    count = 0;
    gameMap = getFrame()
    for y in range(height):
        for x in range(width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                tot_x += location.x
                tot_y += location.y
                count += 1
                go = move(location)
                if go != STILL:
                    moves.append(Move(location, go))
    sendFrame(moves)
    centre_loc.x = tot_x // count
    centre_loc.y = tot_y // count

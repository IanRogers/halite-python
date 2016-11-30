from hlt_orig import *
from networking import *

myID, gameMap = getInit()
width = gameMap.width
width2 = width // 2
height = gameMap.height
height2 = height // 2
max_size = max(width, height) // 1.5

sendInit("Virus2")


def highest_production(strength, min_production, tiles):
    # pick highest production tile we can conquer and we're not already attacking, or stay still to resist
    for who in sorted(tiles, key=lambda who: who[0].production, reverse=True):
        them = who[0]
        if them.location not in attacking:
            if them.strength < strength:
                if them.production >= min_production:
                    return who[1]
    return STILL


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

CORNERS=[(-1, -1), (-1, 1), (1, -1), (1, 1)]
def isTunnel(location):
    x = location.x
    y = location.y
    for dx,dy in CORNERS:
        if gameMap.fetchSite(x + dx, y + dy).owner == myID:
            return False
    return True

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

    strength = site.strength
    if strength == 0:
        # no point trying to move a 0 piece
        return STILL

    if len(enemy) > 0:
        # be agressive if we can, or defend
        edge_runs[location] = (0, STILL)
        return highest_production(strength, 0, enemy)

    if len(blank) > 0:
        # take something if we can, or maybe move elsewhere
        edge_runs[location] = (0, STILL)
        go = highest_production(strength, 0 if strength > 10 else (1 if strength > 5 else 2), blank)
        if go != STILL:
            return go

    if strength < site.production * 6 and strength < 30:
        # just chill dude, you're still growing
        return STILL

    if len(me) == 1:
        if last_count == 2 and count == 2:
            # special case for game start
            return me[0][1]
        else:
            return STILL

    if len(me) == 3:
        # flat edge
        return STILL

    if len(me) == 4:
        # in the middle of a sea of me
        # move to nearest edge
        return nearest_edge(location)[1]

    if len(me) == 2 and isTunnel(location):
        return me[0][1] if me[0][0].strength > me[1][0].strength else me[1][1]

    # corner
    return STILL


last_count = 0
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
                if go != STILL:
                    l = gameMap.getLocation(location, go)
                    if l not in attacking:
                        attacking[l] = location
                        moves.append(Move(location, go))
    sendFrame(moves)
    last_count = count

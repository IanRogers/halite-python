import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, CARDINALS, Move, Square, Run

myID, gameMap = hlt.get_init()
width = gameMap.width
width2 = width // 2
height = gameMap.height
height2 = height // 2
max_size = max(width, height) // 1.5

hlt.send_init("Virus2")


def highest_production(strength, tiles, min_production=0):
    # pick highest production tile we can conquer and we're not already attacking, or stay still to resist
    for who in sorted(tiles, key=lambda who: who[0].production, reverse=True):
        them = who[0]
        if them not in attacking:
            if them.strength < strength:
                if them.production >= min_production:
                    return who
    return (None, STILL)


def nearest_straight_edge(square, heading, lives):
    if square in edge_runs:
        return edge_runs[square][0]
    if square in straight_runs:
        return straight_runs[square]
    if lives < 0:
        return max_size
    if square.owner != myID:
        return -1

    dist = 1 + nearest_straight_edge(gameMap.get_target(square, heading), heading, lives - 1)
    if dist < max_size:
        straight_runs[square] = dist
    return dist

# edges have a distance 0
def nearest_edge(square):
    if square in edge_runs:
        return edge_runs[square]

    go = WEST
    closest = max_size
    tup = (closest, go)

    for d in CARDINALS:
        c = 1 + nearest_straight_edge(gameMap.get_target(square, d), d, closest)
        if c < closest:
            closest = c
            tup = (closest, d)

    # now we have the real value
    edge_runs[square] = tup
    return tup

def move(square):
    strength = square.strength
    if strength == 0:
        # no point trying to move a 0 piece
        return STILL

    blank = []
    enemy = []
    me = []
    for d in CARDINALS:
        them = gameMap.get_target(square, d)
        who = (them, d)
        owner = them.owner
        if owner == 0:
            blank.append(who)
        elif owner == myID:
            me.append(who)
        else:
            enemy.append(who)

    if len(enemy) > 0:
        # be agressive if we can, or defend
        edge_runs[square] = (0, STILL)
        return highest_production(strength, enemy, 0)[1]

    if len(blank) > 0:
        # take something if we can, or maybe move elsewhere
        edge_runs[square] = (0, STILL)
        target, go = highest_production(strength, blank, 0 if strength > 10 else (1 if strength > 5 else 2))
        if go != STILL:
            return go

    if strength < square.production * 6 and strength < 30:
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
        return nearest_edge(square)[1]

    if len(me) == 2 and gameMap.isTunnel(square):
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
    gameMap.get_frame()
    for square in gameMap:
        if square.owner == myID:
            count += 1
            go = move(square)
            if go != STILL:
                l = gameMap.get_target(square, go)
                if l not in attacking:
                    attacking[l] = square
                    hlt.send_move(Move(square, go))
    hlt.end_frame()
    last_count = count

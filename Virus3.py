import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, CARDINALS, Move, Square, Run

myID, gameMap = hlt.get_init()
last_count = 0

hlt.send_init("Virus3")


def highest_production(strength, tiles, min_production=0) -> int:
    "pick highest production tile we can conquer, or stay still to resist"
    target, direction = max((tile for tile in tiles if tile[0].strength < strength and tile[0].production >= min_production),
                            default=(None, STILL),
                            key=lambda t: t[0].production)
    return direction

def move(square:Square) -> int:
    strength = square.strength
    if strength == 0:
        # no point trying to move a 0 piece
        return STILL

    blank = []
    enemy = []
    me = []
    danger = False
    for d in CARDINALS:
        them = gameMap.get_target(square, d)
        owner = them.owner
        if owner == myID:
            me.append((them, d))
        else:
            if strength > them.strength:
                if owner == 0:
                    blank.append((them, d))
                else:
                    danger = True
                    enemy.append((them, d))

    if danger or enemy != []:
        # be agressive if we can, or defend
        return max(enemy, default=(None, STILL), key=lambda e: gameMap.overkill(e[0]))[1]

    if blank != []:
        # take something if we can, or maybe move along the edge
        go = max(blank, key=lambda b: b[0].production)[1]
        if go != STILL:
            return go

    if strength < square.production * 6 and strength < 30:
        # just chill dude, you're still growing
        return STILL

    if len(me) == 1:
        # end piece
        if last_count == 2 and count == 2:
            # special case for game start
            return me[0][1]
        else:
            return STILL
    elif len(me) == 4:
        # in the middle of a sea of me
        # move to nearest edge
        return gameMap.nearest_edge_direction(square)
    elif len(me) == 2 and gameMap.isTunnel(square):
        return me[0][1] if me[0][0].strength > me[1][0].strength else me[1][1]

    # corner or flat edge
    return STILL

def best_attacker(attacking_me) -> Move:
    assert attacking_me != []
    return max(attacking_me, key=lambda a: a[0].strength)

while True:
    count = 0
    moves = []
    gameMap.get_frame()
    for square in gameMap:
        if square.owner == myID:
            count += 1
            d = move(square)
            if d != STILL:
                target = gameMap.get_target(square, d)
                target.attacking_me.append(Move(square, d))

    for square in gameMap:
        att = square.attacking_me
        if att != []:
            total = 0;
            for m in sorted(att, key=lambda m: m.square.strength, reverse=True):
                hlt.send_move(m)
                total += m.square.strength
                if total > 255:
                    break

    hlt.end_frame()
    last_count = count


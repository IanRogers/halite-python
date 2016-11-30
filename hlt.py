"""
A Python-based Halite starter-bot framework.

This module contains a Pythonic implementation of a Halite starter-bot framework.
In addition to a class (GameMap) containing all information about the game world
and some helper methods, the module also implements the functions necessary for
communicating with the Halite game environment.
"""

import sys
from collections import namedtuple
from itertools import chain, zip_longest


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

# Because Python uses zero-based indexing, the cardinal directions have a different mapping in this Python starterbot
# framework than that used by the Halite game environment.  This simplifies code in several places.  To accommodate
# this difference, the translation to the indexing system used by the game environment is done automatically by
# the send_frame function when communicating with the Halite game environment.

NORTH, EAST, SOUTH, WEST, STILL = range(5)
CARDINALS = [NORTH, EAST, SOUTH, WEST]

def opposite_cardinal(direction):
    "Returns the opposing cardinal direction."
    return (direction + 2) % 4 if direction != STILL else STILL

Move = namedtuple('Move', 'square direction')
Run = namedtuple('Run', 'distance direction')

class Square:
    def __init__(self, x, y, owner, strength, production, edge_run:Run=None):
        self.x = x
        self.y = y
        self.owner = owner
        self.strength = strength
        self.production = production
        self.edge_run = edge_run
        self.attacking_me = []



class GameMap:
    def __init__(self, size_string, production_string, my_id, map_string=None):
        self.width, self.height = tuple(map(int, size_string.split()))
        self.max_side = max(self.width, self.height)
        self.production = tuple(tuple(map(int, substring)) for substring in grouper(production_string.split(), self.width))
        self.contents = None
        self.my_id = my_id
        self.get_frame(map_string)
        self.starting_player_count = len(set(square.owner for square in self)) - 1

    def get_frame(self, map_string=None):
        "Creates new map from the latest frame provided by the Halite game environment."
        if map_string is None:
            map_string = get_string()
        split_string = map_string.split()
        owners = list()
        while len(owners) < self.width * self.height:
            counter = int(split_string.pop(0))
            owner = int(split_string.pop(0))
            owners.extend([owner] * counter)
        assert len(owners) == self.width * self.height
        assert len(split_string) == self.width * self.height
        self.contents = [[Square(x, y, owner, strength, production)
                          for x, (owner, strength, production)
                          in enumerate(zip(owner_row, strength_row, production_row))]
                         for y, (owner_row, strength_row, production_row)
                         in enumerate(zip(grouper(owners, self.width),
                                          grouper(map(int, split_string), self.width),
                                          self.production))]

    def __iter__(self):
        "Allows direct iteration over all squares in the GameMap instance."
        return chain.from_iterable(self.contents)

    def neighbors(self, square, n=1, include_self=False):
        "Iterable over the n-distance neighbors of a given square.  For single-step neighbors, the enumeration index provides the direction associated with the neighbor."
        assert isinstance(include_self, bool)
        assert isinstance(n, int) and n > 0
        if n == 1:
            combos = ((0, -1), (1, 0), (0, 1), (-1, 0), (0, 0))   # NORTH, EAST, SOUTH, WEST, STILL ... matches indices provided by enumerate(game_map.neighbors(square))
        else:
            combos = ((dx, dy) for dy in range(-n, n+1) for dx in range(-n, n+1) if abs(dx) + abs(dy) <= n)
        return (self.contents[(square.y + dy) % self.height][(square.x + dx) % self.width] for dx, dy in combos if include_self or dx or dy)

    def get_target(self, square:Square, direction:int) -> Square:
        "Returns a single, one-step neighbor in a given direction."
        dx, dy = ((0, -1), (1, 0), (0, 1), (-1, 0), (0, 0))[direction]
        return self.contents[(square.y + dy) % self.height][(square.x + dx) % self.width]

    def get_square(self, x, y) -> Square:
        return self.contents[y % self.height][x % self.width]

    def get_distance(self, sq1, sq2):
        "Returns Manhattan distance between two squares."
        dx = min(abs(sq1.x - sq2.x), sq1.x + self.width - sq2.x, sq2.x + self.width - sq1.x)
        dy = min(abs(sq1.y - sq2.y), sq1.y + self.height - sq2.y, sq2.y + self.height - sq1.y)
        return dx + dy

    def nearest_straight_distance(self, square:Square, heading:int, lives:int) -> int:
        if square.edge_run != None:
            return square.edge_run.distance
        if lives < 0:
            return self.max_side
        if square.owner != self.my_id:
            return -1

        dist = 1 + self.nearest_straight_distance(self.get_target(square, heading), heading, lives - 1)
        if dist < self.max_side:
            square.edge_run = Run(distance=dist, direction=heading)
        return dist

    def nearest_edge_direction(self, square:Square) -> int:
        "edges have a distance 0"
        if square.edge_run != None:
            return square.edge_run.direction

        go = WEST
        closest = self.max_side
        run = Run(distance=closest, direction=go)

        for d in CARDINALS:
            c = 1 + self.nearest_straight_distance(self.get_target(square, d), d, closest)
            if c < closest:
                closest = c
                run = Run(distance=closest, direction=d)

        # cache the run
        square.edge_run = run
        return run.direction

    def overkill(self, square:Square) -> int:
        return sum(neighbor.strength for neighbor in self.neighbors(square) if neighbor.owner not in (0, self.my_id))

    def isTunnel(self, square:Square):
        "I only have me at flat edges"
        x = square.x
        y = square.y
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if self.get_square(x + dx, y + dy).owner == self.my_id:
                return False
        return True

#####################################################################################################################
# Functions for communicating with the Halite game environment (formerly contained in separate module networking.py #
#####################################################################################################################


def send_string(s):
    sys.stdout.write(s)
    sys.stdout.write('\n')
    sys.stdout.flush()


def get_string():
    return sys.stdin.readline().rstrip('\n')


def get_init() -> (int, GameMap):
    playerID = int(get_string())
    m = GameMap(get_string(), get_string(), playerID)
    return playerID, m


def send_init(name):
    send_string(name)


def translate_cardinal(direction):
    "Translate direction constants used by this Python-based bot framework to that used by the official Halite game environment."
    # Cardinal indexing used by this bot framework is
    #~ NORTH = 0, EAST = 1, SOUTH = 2, WEST = 3, STILL = 4
    # Cardinal indexing used by official Halite game environment is
    #~ STILL = 0, NORTH = 1, EAST = 2, SOUTH = 3, WEST = 4
    #~ >>> list(map(lambda x: (x+1) % 5, range(5)))
    #~ [1, 2, 3, 4, 0]
    return (direction + 1) % 5

def send_move(move:Move):
    sys.stdout.write(str(move.square.x) + ' ' + str(move.square.y) + ' ' + str(translate_cardinal(move.direction)) + ' ')

def end_frame():
    sys.stdout.write('\n')
    sys.stdout.flush()

def send_frame(moves):
    for m in moves:
        send_move(m)
    end_frame()

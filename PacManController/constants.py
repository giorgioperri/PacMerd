from vector import Vector2

TILEWIDTH = 16
TILEHEIGHT = 16
NROWS = 36
NCOLS = 28
SCREENWIDTH = NCOLS*TILEWIDTH
SCREENHEIGHT = NROWS*TILEHEIGHT
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT)

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255,100,150)
TEAL = (100,255,255)
ORANGE = (230,190,40)
GREEN = (0, 255, 0)

STOP = 0
UP = 1
DOWN = -1
LEFT = 2
RIGHT = -2
PORTAL = 3

# An array of nodes to ignore when calculating the shortest path
NODES_TO_IGNORE = [
  Vector2(184.0, 256.0),
  Vector2(184.0, 272.0),
  Vector2(184.0, 288.0),
  Vector2(248.0, 256.0),
  Vector2(248.0, 288.0),
  Vector2(248.0, 272.0),
  Vector2(216.0, 272.0),
  Vector2(144.0, 224.0),
  Vector2(240.0, 224.0),
  Vector2(288.0, 224.0),
  Vector2(144.0, 272.0),
  Vector2(144.0, 320.0),
  Vector2(192.0, 224.0),
  Vector2(288.0, 272.0),
  Vector2(288.0, 320.0),
  Vector2(432.0, 272.0),
  Vector2(0.0, 272.0),
  Vector2(216.0, 224.0)
]

PACMAN = 0
PELLET = 1
POWERPELLET = 2
GHOST = 3
BLINKY = 4
PINKY = 5
INKY = 6
CLYDE = 7
FRUIT = 8

SCATTER = 0
CHASE = 1
FREIGHT = 2
SPAWN = 3

SCORETXT = 0
LEVELTXT = 1
READYTXT = 2
PAUSETXT = 3
GAMEOVERTXT = 4

# The distance at which a ghost will be considered "nearby"
GHOST_NEARBY_DISTANCE = 75
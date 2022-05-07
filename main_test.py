from time import sleep
import pygame
from utils import *
from shapely.geometry import Polygon
from GameEnviroment import *

env = GameEnviroment()
while env.is_done() != True:
    env.render()
    sleep(0.5)
    # env.car1.turn(1)
    # env.car1.update()
    env.car1.actionTaken((2,2))
    env.car1.getAllDistances(env.walls)
# windows = pygame.display.set_mode((1200,700))

# p1 = Polygon([(0,0), (1,1)])
# p2 = Polygon([(2,2), (3,3), (4,4)])
# print(p1.intersects(p2))

# p = Point(3,5)
# p1 = Point(10,6)
# print(p.distanceTo(p1))
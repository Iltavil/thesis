
from time import sleep
import numpy as np
import pygame
from utils import *
from shapely.geometry import Polygon
from GameEnvironment import *
from gym.spaces import Discrete, Tuple, Box

from Environment import *


# env = Environment()
# print(env.observe(env.environment.cars[0]))
# print(env.observation_space(env.environment.cars[0]))
# env.step(7)


env = GameEnvironment()
while env.is_done() != True:
    env.render()
    env.userInput()
    print(env.observe(0))
#     for i in range(4):
#         r = env.step(i+1,0)
 
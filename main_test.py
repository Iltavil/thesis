
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
while not env.is_done():
    sleep(0.1)
    env.render()
    env.userInput()
    env.observe(1)
#     for i in range(4):
#         r = env.step(i+1,0)
 
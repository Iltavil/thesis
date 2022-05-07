import pygame
from WindowElement import WindowElement
from utils import *
from Point import *
class Wall:
    def __init__(self, point1:list,point2:list):
        self.points = []
        self.points.append(point1)
        self.points.append(point2)



    def draw(self, window):
        pygame.draw.line(window, color_black, self.points[0], self.points[1],3)

        
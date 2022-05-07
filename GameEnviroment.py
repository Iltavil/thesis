import pygame
from Wall import Wall
from utils import *
from Car import Car


class GameEnviroment:
    def __init__(self):
        pygame.init()

        self.width = windowWidth
        self.height = windowHeight
        self.fps = 60
        self.font = pygame.font.SysFont("Times New Roman", 18)
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.width,self.height))
        self.done = False

        self.walls = []
        self.createWalls()

        #we will have 4 cars
        self.car1 = Car(300,300)


    def createWalls(self):
        self.walls.append(Wall([50,50],[100,600]))
        self.walls.append(Wall([400,50],[400,600]))
        self.walls.append(Wall([1,1],[1,self.height]))
        self.walls.append(Wall([1,1],[self.width,1]))
        self.walls.append(Wall([self.width,1],[self.width,self.height]))
        self.walls.append(Wall([1,self.height],[self.width,self.height]))

    def checkWalls(self):
        #TODO add index for car that hits wall
        # print(self.car1.hitAllWalls(self.walls))
        pass



    def renderWalls(self):
        for wall in self.walls:
            wall.draw(self.window)

    def render(self):
        self.window.fill(color_green)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done= True


        self.car1.render(self.window)
        self.car1.renderSight(self.window)
        self.renderWalls()

        pygame.display.flip()
        self.clock.tick(self.fps)

    def is_done(self):
        return self.done


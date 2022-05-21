from operator import index
from re import S
import pygame
from Wall import Wall
from utils import *
from Car import Car
import numpy as np
from gym.spaces import Box


class GameEnvironment:
    def __init__(self):
        pygame.init()

        self.width = windowWidth
        self.height = windowHeight
        self.fps = 60
        self.font = pygame.font.SysFont("Times New Roman", 18)
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.width,self.height))
        self.done = False
        
        self.resetPoints = [(300,500),(894, 107),(86, 285),(900, 482),(447,161),(580,550),(1050,250),(1104,432)]

        self.walls = []
        self.createWalls()

        #we will have 4 cars
        self.cars = []
        self.cars.append(Car(447,161,self.walls,self.resetPoints))
        self.cars.append(Car(300,500,self.walls,self.resetPoints))
        self.cars.append(Car(580,550,self.walls,self.resetPoints))
        self.cars.append(Car(1050,250,self.walls,self.resetPoints))
        self.cars.append(Car(1104,432,self.walls,self.resetPoints))

        for i in range(len(self.cars)):
            self.cars[i].setCars(self.cars,i)

        

        self.setInitialTargets()
        #start game timer after init
        self.startTime = pygame.time.get_ticks()
        

    def setInitialTargets(self):
        for i in range(len(self.cars)):
            j = (i+1) % len(self.cars)
            self.cars[i].setTarget(j)



    def createWalls(self):
        self.walls.append(Wall([1,1],[1,self.height]))
        self.walls.append(Wall([1,1],[self.width,1]))
        self.walls.append(Wall([self.width,1],[self.width,self.height]))
        self.walls.append(Wall([1,self.height],[self.width,self.height]))
        self.walls.append(Wall((196, 312),(462, 305)))
        self.walls.append(Wall((575, 268),(576, 101)))
        self.walls.append(Wall((446, 474),(443, 392)))
        self.walls.append(Wall((713, 405),(443, 392)))
        self.walls.append(Wall((222, 208),(394, 60)))
        self.walls.append(Wall((806, 261),(809, 478)))
        self.walls.append(Wall((622, 476),(818, 596)))
        self.walls.append(Wall((166, 602),(178, 489)))
        self.walls.append(Wall((166, 602),(332, 601)))
        self.walls.append(Wall((1092, 345),(1139, 292)))
        self.walls.append(Wall((1131, 173),(1089, 96)))
        self.walls.append(Wall((971, 368),(1066, 418)))
        self.walls.append(Wall((1045, 555),(1250, 407)))


    def checkWalls(self,index):
        #TODO add index for car that hits wall
        print(self.cars.hitAllWalls(self.walls))
        pass

    def observe(self, index):
        sightResult = self.cars[index].getAllDistances()
        sightResult.append(self.cars[index].seeTarget())
        sightResult = np.array(np.concatenate(sightResult).flat, dtype=np.int64)
        return sightResult



    def renderWalls(self):
        for wall in self.walls:
            wall.draw(self.window)

    def render(self):
        self.window.fill(color_green)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done= True
            if event.type == pygame.MOUSEBUTTONUP:
                print(pygame.mouse.get_pos())
                pass
        


        for car in self.cars:
            car.render(self.window)
        # for car in self.cars:
        #     car.renderSight(self.window)
        self.renderWalls()

        pygame.display.flip()
        self.clock.tick(self.fps)

    def userInput(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            if keys[pygame.K_a]:
                action = 5
            elif keys[pygame.K_d]:
                action = 6
            else:
                action = 1
        elif keys[pygame.K_s]:
            if keys[pygame.K_a]:
                action = 7
            elif keys[pygame.K_d]:
                action = 8
            else:
                action = 2
        elif keys[pygame.K_a]:
            action = 3
        elif keys[pygame.K_d]:
            action = 4
        else:
            action = 0

        r = self.step(0,action)
        # if r != 0:
        # print(r)

    def step(self,carIndex,action):
        if self.startTime - pygame.time.get_ticks() > gameTime:
            self.is_done = True
        self.cars[carIndex].wasHitBeforeStep()
        self.cars[carIndex].translateAction(action)
        self.cars[carIndex].hitAllWalls()
        self.cars[carIndex].hitAllCars()
        return self.cars[carIndex].stepScore


    def is_done(self):
        return self.done

    def reset(self):
        for car in self.cars:
            car.reset()
        for i in range(len(self.cars)):
            self.cars[i].setCars(self.cars,i)
        self.setInitialTargets()
        self.startTime = pygame.time.get_ticks()


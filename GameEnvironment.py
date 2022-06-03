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
        

        self.width = windowWidth
        self.height = windowHeight
        self.fps = 60
        
        
        self.done = False
        self.doneCars = 0
        
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
        self.carSteps = []
        self.carScores = []

        for i in range(len(self.cars)):
            self.cars[i].setCars(self.cars,i)
            self.carSteps.append(0)
            self.carScores.append(0)

        

        self.setInitialTargets()
        #start game timer after init
        # self.startTime = pygame.time.get_ticks()
        

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



    def observe(self, index):
        sightResult = self.cars[index].getAllDistances()
        sightResult.append(self.cars[index].seeTarget())
        sightResult = np.array(np.concatenate(sightResult).flat, dtype=np.int64)
        sightResult = np.insert(sightResult,0, self.cars[index].velocity)
        sightResult = np.insert(sightResult,1, vectorToAngle(self.cars[index].direction))
        return sightResult



    def renderWalls(self):
        for wall in self.walls:
            wall.draw(self.window)

    def render(self):
        pygame.init()
        # self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.width,self.height))
        self.window.fill(color_green)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done= True
            if event.type == pygame.MOUSEBUTTONUP:
                # print(pygame.mouse.get_pos())
                pass
        


        for i in range(len(self.cars)):
            if not self.carIsDone(i):
                self.cars[i].render(self.window)
        # for car in self.cars:
        #     car.renderSight(self.window)
        self.renderWalls()

        pygame.display.flip()
        # self.clock.tick(self.fps)

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

        i = 1
        while self.carIsDone(i) == True:
            i += 1
        r = self.step(i,action)
        # if r != 0:
        # print(r)

    def step(self,carIndex,action):
        #TODO change the error type
        if self.carIsDone(carIndex):
            raise ValueError("car is done, but action taken")
        self.carSteps[carIndex] += 1
        #end in case of timeout
        if self.carSteps[carIndex] > carMaxSteps:
            self.cars[carIndex].stillAlive = False
        self.cars[carIndex].wasHitBeforeStep()
        self.cars[carIndex].translateAction(action)
        self.cars[carIndex].hitAllWalls()
        self.cars[carIndex].hitAllCars()
        # self.observe(carIndex)
        self.cars[carIndex].scoreSeeTarget()
        #make car be done
        if self.carIsDone(carIndex):
            self.doneCars += 1
        #end in case all cars are done
        if self.doneCars == len(self.cars) - 1:
            self.done = True
        # self.render()
        self.carScores[carIndex] = self.cars[carIndex].stepScore
        return self.cars[carIndex].stepScore
        

    def carIsDone(self,carIndex):
        return not self.cars[carIndex].stillAlive


    def is_done(self):
        return self.done

    def reset(self):
        for car in self.cars:
            car.reset()
        self.carSteps = []
        self.carScores = []
        for i in range(len(self.cars)):
            self.cars[i].setCars(self.cars,i)
            self.carSteps.append(0)
            self.carScores.append(0)
        self.done = False
        self.doneCars = 0
        self.setInitialTargets()
        # self.startTime = pygame.time.get_ticks()


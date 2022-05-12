from re import S
import pygame
from WindowElement import WindowElement
from utils import *
from shapely.geometry import Point, LineString, Polygon


class Car(WindowElement):
    def __init__(self,xCenter,yCenter):
        super().__init__()

        self.xCenter = xCenter
        self.yCenter = yCenter
        self.originPoint = (xCenter,yCenter)
        self.previousPoint = (xCenter,yCenter)
        self.direction = pygame.Vector2(0,1)
        self.corners = []
        self.visionDistances = []
        self.lineCollisionPoints = []
        self.hitCar = False
        self.polygon = None
        self.getCorners()
        
        
        #all cars should have an index
        self.targetIndex = -1

        self.image = pygame.image.load("car.svg")
        self.image = pygame.transform.scale(self.image, (carLength,carWidth))

        self.velocity = 0
        self.driftMomentum = 0

    def setTarget(self, targetIndex):
        self.targetIndex = targetIndex

    def resetWithAnotherPosition(self,resetPoints):
        resetPoint = resetPoints[0]
        self.reset()
        self.xCenter = resetPoint[0]
        self.yCenter = resetPoint[1]

    def reset(self):   
        self.xCenter = self.originPoint[0]
        self.yCenter = self.originPoint[1]
        self.previousPoint = (self.xCenter,self.yCenter)
        self.direction = pygame.Vector2(0,1)
        self.corners = []
        self.visionDistances = []
        self.lineCollisionPoints = []
        self.velocity = 0
        self.driftMomentum = 0
        self.hitCar = False
        self.getCorners()



    def render(self,window):
        #
        angle = vectorToAngle(self.direction)
        image_rect = self.image.get_rect(topleft = (self.xCenter - carLength/2, self.yCenter - carWidth/2))
        offset_center_to_pivot = pygame.math.Vector2(self.xCenter,self.yCenter) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(angle)
        rotated_image_center = (self.xCenter - rotated_offset.x, self.yCenter - rotated_offset.y)
        rotated_image = pygame.transform.rotate(self.image, -angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        window.blit(rotated_image,rotated_image_rect)

    def renderSight(self,window):
        for sightLine in self.lineCollisionPoints:
            if sightLine[1] == (0,0):
                continue
            pygame.draw.circle(window,color_blue,sightLine[1],3)
            pygame.draw.line(window, color_blue, sightLine[0], sightLine[1],1)

    #update the position 
    def update(self):
        #we create a vector to calculate added x and y position based on current position and angle
        addedVector = pygame.Vector2(0,0)
        addedVector.x += self.velocity * self.direction.x
        addedVector.y += self.velocity * self.direction.y

        # #drift 
        # driftVector = pygame.Vector2(self.direction)
        # driftVector =driftVector.rotate(90)
        # addedVector.x += self.driftMomentum * driftVector.x
        # addedVector.x += self.driftMomentum * driftVector.y
        # self.driftMomentum *= driftFriction


        # if addedVector.length() != 0:
        #     addedVector.normalize()
        # addedVector.x *= abs(self.velocity)
        # addedVector.y *= abs(self.velocity)
        self.previousPoint = (self.xCenter,self.yCenter)
        self.xCenter += addedVector.x
        self.yCenter += addedVector.y



    #action is a tuple of form(a,b), where
    #a = 0->nothing, a = 1 ->accelerate, a = 2 ->break/reverse
    #b = 0->nothing, a = 1 ->left, a = 2 ->right
    #
    def actionTaken(self,action):
        accelerate = action[0]
        angleTaken = action[1]

        if accelerate == 1:
            self.accelerateCar()
        elif accelerate == 2:
            self.decelerateCar()

        if angleTaken == 1:
            self.turn(-1)
        elif angleTaken == 2:
            self.turn(1)


        self.update()


    #we accelerate from 0 or break from reverse to 0 speed
    def accelerateCar(self):
        if self.velocity >= 0:
            self.velocity += carForwardAcceleration
            if self.velocity >= carMaxSpeed:
                self.velocity = carMaxSpeed
        else:
            self.velocity += carBreak
            if self.velocity >=0:
                self.velocity = 0

    def getCorners(self):
        directionVector = pygame.Vector2(self.direction)
        normalVector = pygame.Vector2(self.direction).rotate(-90)
        cornerMultipliers = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
        carPosition = pygame.Vector2(self.xCenter,self.yCenter)
        self.corners = []
        for i in range(4):
            self.corners.append(carPosition + (directionVector * carLength / 2 * cornerMultipliers[i][0]) +
                              (normalVector * carWidth / 2 * cornerMultipliers[i][1]))
        self.polygon = Polygon(self.corners)


    def hitWall(self, wall):
        for i in range(4):
            j = (i+1)%4
            if linesIntersect(wall.points[0],wall.points[1],(self.corners[i].x,self.corners[i].y),(self.corners[j].x,self.corners[j].y)):
                self.xCenter = self.previousPoint[0]
                self.yCenter = self.previousPoint[1]
                self.velocity = 0
                return True
        return False
    
    def hitAllWalls(self, walls):
        self.getCorners()
        for wall in walls:
            if self.hitWall(wall):
                return True
        return False

    def hitAllCars(self,cars,selfIndex):
        #check if it hits another car
        self.getCorners()
        for i in range(len(cars)):
            if i == selfIndex:
                continue
            return self.polygon.intersects(cars[i].polygon)
            

    #we decelerate from 0 or break from forward to 0 speed
    def decelerateCar(self):
        if self.velocity <= 0:
            self.velocity -= carReverseAcceleration
            if self.velocity <= carMaxSpeedReverse:
                self.velocity = carMaxSpeedReverse
        else:
            self.velocity -= carBreak
            if self.velocity <=0:
                self.velocity = 0

    #turnDirection is -1 for left and 1 for right
    def turn(self, turnDirection):
        # slowSpeedMultiplier is 1 for high speeds and lower for low speeds
        slowSpeedMultiplier = 1
        if abs(self.velocity) < carMaxSpeed/3:
            slowSpeedMultiplier = abs(self.velocity)/(carMaxSpeed/3)
        if self.velocity < 0:
            slowSpeedMultiplier *= 1

        # drift
        # drift = self.velocity * angleToRadians(turningAngle)
        # if self.velocity < carMaxSpeed/3:
        #     drift = 0
        # self.driftMomentum += drift
        
        #turn
        self.direction = self.direction.rotate(turnDirection * turningAngle * slowSpeedMultiplier)


    #have the distance vectors here
    def getAllDistances(self,walls):
        self.visionDistances = []
        self.lineCollisionPoints = []
        #set side vectors
        sightAngles = [0,20,45,75,105]
        for angle in sightAngles:
            self.getDistanceFromVector(carLength/2,carWidth/2,angle,walls)
            self.getDistanceFromVector(carLength/2,-carWidth/2,-angle,walls)



    def getDistanceFromVector(self,x,y,angle,walls):
        originPoint = self.getPositionRelativeToRotationAngle(x,y)
        visionVectorDirection = self.direction.rotate(angle).normalize() * carVisionMaxRange
        closestPoint,smallestDistance = self.getClosestHitToWall(originPoint,(originPoint[0] + visionVectorDirection[0],originPoint[1] + visionVectorDirection[1]), walls)
        
        self.lineCollisionPoints.append((originPoint,(closestPoint.x,closestPoint.y)))
        if closestPoint.x == 0 and closestPoint.y == 0:
            self.visionDistances.append(carVisionMaxRange)
        else:
            self.visionDistances.append(smallestDistance)
        


    def getPositionRelativeToRotationAngle(self,x,y):
        #receives a position on the car
        #returns a vector with the position on the surface
        directionVector = pygame.Vector2(self.direction).normalize()
        normalVector = self.direction.rotate(90).normalize()
        return pygame.Vector2(self.xCenter,self.yCenter) +((directionVector * x) + (normalVector * y))

    def getClosestHitToWall(self, point1, point2, walls):
        #given a line and the walls, find the intersection with the closest wall
        #returns the point and the distance
        closestWallHit = pygame.Vector2(0,0)
        minDistance = 2 * min(windowHeight, windowWidth)
        

        for wall in walls:
            line1 = LineString([Point(point1),Point(point2)])
            line2 = LineString([Point(wall.points[0]),Point(wall.points[1])])
            collisionPoint = line1.intersection(line2)
            
            if collisionPoint.is_empty:
                continue
            collisionPoint = (collisionPoint.x,collisionPoint.y)
            # collisionPoint = lineIntersectionPoint(point1,point2,wall.points[0],wall.points[1])
            

            distanceToWall = distanceBetweenPoints(point1,collisionPoint)
            if distanceToWall < minDistance:
                minDistance = distanceToWall
                closestWallHit = Vector2(collisionPoint)
        return closestWallHit,minDistance


            
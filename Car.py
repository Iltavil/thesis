import pygame

from utils import *
from shapely.geometry import Point, LineString, Polygon
from numpy import mean
from random import choice


class Car():
    def __init__(self,xCenter,yCenter,walls,resetPoints):
        super().__init__()

        self.image = None

        self.xCenter = xCenter
        self.yCenter = yCenter
        self.previousPoint = (xCenter,yCenter)
        self.direction = pygame.Vector2(0,1)
        self.previousDirection = self.direction
        self.corners = []
        self.visionDistances = []
        self.lineCollisionPoints = []
        #0/wallType for wall, 1/carType for car
        self.lineCollisionPointsType = []
        self.wasHit = False
        self.wasHitByTarget = False
        self.wasHitByHunter = False
        self.polygon = None
        self.velocity = 0
        self.hitWallBug = 0
        self.angleToTarget = 106
        self.distanceToTarget = carVisionMaxRange
        self.previousAngleToTarget = 106
        self.previousDistanceToTarget = carVisionMaxRange

        self.distanceBetweenHunterAndTarget = windowWidth + windowHeight

        self.lives = carMaxLives
        self.stillAlive = True

        self.score = 0
        self.stepScore = 0
        self.getCorners()
        
        
        #all cars should have an index
        self.targetIndex = -1

        


        #should not be modified after initialised
        self.originPoint = (xCenter,yCenter)

        self.walls = walls
        self.allCars = []
        self.resetPoints = resetPoints
        self.ownIndex = -1

    def setWalls(self, walls):
        self.walls = walls
        

    #sets the target of this car
    #it needs to be called by main function after it hits its target
    def setTarget(self, targetIndex):
        self.targetIndex = targetIndex



    #sets all cars, needs to be called after all cars were initialised
    def setCars(self, allCars, ownIndex):
        self.allCars = allCars
        self.ownIndex = ownIndex

    def checkResetPoint(self,resetPoint):
        self.xCenter = resetPoint[0]
        self.yCenter = resetPoint[1]
        self.getCorners()
        for i in range(len(self.allCars)):
            if i == self.ownIndex:
                continue
            if self.polygon.intersects(self.allCars[i].polygon):
                return False
        return True

    #resets the car and chenges the position to a random one
    def resetWithAnotherPosition(self):
        self.lives -= 1
        if self.lives == 0:
            self.stillAlive = False

        resetPoint = choice(self.resetPoints)
        while not self.checkResetPoint(resetPoint):
            resetPoint = choice(self.resetPoints)
        self.partialReset()
        self.xCenter = resetPoint[0]
        self.yCenter = resetPoint[1]
        
        self.previousPoint = (self.xCenter,self.yCenter)

    def reset(self):
        self.score = 0
        self.stepScore = 0
        self.lives = carMaxLives
        self.stillAlive = True
        self.partialReset()


    #fully resets the car, when the game is restarted
    def partialReset(self):   
        self.xCenter = self.originPoint[0]
        self.yCenter = self.originPoint[1]
        self.previousPoint = (self.xCenter,self.yCenter)
        self.direction = pygame.Vector2(0,1)
        self.previousDirection = self.direction
        self.corners = []
        self.visionDistances = []
        self.lineCollisionPoints = []
        self.lineCollisionPointsType = []
        self.velocity = 0
        self.wasHit = False
        self.wasHitByTarget = False
        self.wasHitByHunter = False
        self.hitWallBug = 0
        self.angleToTarget = 106
        self.distanceToTarget = carVisionMaxRange
        self.previousAngleToTarget = 106
        self.previousDistanceToTarget = carVisionMaxRange
        self.distanceBetweenHunterAndTarget = windowWidth + windowHeight
        self.getCorners()



    def render(self,window):
        #renders the car on the given surface, after rotating the image
        angle = vectorToAngle(self.direction)
        if self.image == None:
            self.image = pygame.image.load("images\car.png")
            self.image = pygame.transform.scale(self.image, (carLength,carWidth))
        image_rect = self.image.get_rect(topleft = (self.xCenter - carLength/2, self.yCenter - carWidth/2))
        offset_center_to_pivot = pygame.math.Vector2(self.xCenter,self.yCenter) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(angle)
        rotated_image_center = (self.xCenter - rotated_offset.x, self.yCenter - rotated_offset.y)
        rotated_image = pygame.transform.rotate(self.image, -angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        window.blit(rotated_image,rotated_image_rect)
        # for corner in self.corners:
        #     pygame.draw.circle(window,color_black,corner,2)

    def renderSight(self,window):
        #renders the sight vectors and the collision points
        for i in range(len(self.lineCollisionPoints)):
            if self.lineCollisionPoints[i][1] == (0,0):
                continue
            if self.lineCollisionPointsType[i] == wallType:
                colorUsed = color_blue
            else:
                colorUsed = color_red
            pygame.draw.circle(window,colorUsed,self.lineCollisionPoints[i][1],3)
            pygame.draw.line(window, colorUsed, self.lineCollisionPoints[i][0], self.lineCollisionPoints[i][1],1)

    #update the position of the car in the 2D plane
    def update(self):
        #we create a vector to calculate added x and y position based on current position and angle
        
        self.velocity *= friction
        addedVector = pygame.Vector2(0,0)
        addedVector.x += self.velocity * self.direction.x
        addedVector.y += self.velocity * self.direction.y


        self.previousPoint = (self.xCenter,self.yCenter)
        self.xCenter += addedVector.x
        self.yCenter += addedVector.y

        self.getCorners()

    #we receive one number for action between 0 and 8 and translate it to a tuple:
    #0 - do nothing
    #1 - forward
    #2 - reverse
    #3 - left 
    #4 - right
    #5 - forward left 
    #6 - forward right
    #7 - reverse left 
    #8 - reverse right
    def translateAction(self,action):
        if action == 0:
            self.actionTaken((0,0))
        elif action == 1:
            self.actionTaken((1,0))
        elif action == 2:
            self.actionTaken((2,0))
        elif action == 3:
            self.actionTaken((0,1))
        elif action == 4:
            self.actionTaken((0,2))
        elif action == 5:
            self.actionTaken((1,1))
        elif action == 6:
            self.actionTaken((1,2))
        elif action == 7:
            self.actionTaken((2,1))
        elif action == 8:
            self.actionTaken((2,2))




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
    #turns the car angle clockwise or counterclockwise
    def turn(self, turnDirection):
        # slowSpeedMultiplier is 1 for high speeds and lower for low speeds
        slowSpeedMultiplier = 1
        if abs(self.velocity) < carMaxSpeed/3:
            slowSpeedMultiplier = abs(self.velocity)/(carMaxSpeed/3)
        if self.velocity < 0:
            slowSpeedMultiplier *= 1
        
        self.previousDirection = self.direction
        self.direction = self.direction.rotate(turnDirection * turningAngle * slowSpeedMultiplier)

    #calculates the corners of the car, used to find intersections
    def getCorners(self):
        cornerMultipliers = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
        self.corners = []
        for i in range(4):
            self.corners.append(self.getPositionRelativeToRotationAngle(carLength / 2 * cornerMultipliers[i][0],carWidth / 2 * cornerMultipliers[i][1]))
        self.polygon = Polygon(self.corners)


    #checks if the car intersects with the wall by checking all sides against the wall
    def hitWall(self, wall):
        for i in range(4):
            j = (i+1)%4
            if linesIntersect(wall.points[0],wall.points[1],(self.corners[i].x,self.corners[i].y),(self.corners[j].x,self.corners[j].y)):
                self.xCenter = self.previousPoint[0]
                self.yCenter = self.previousPoint[1]
                self.direction = self.previousDirection
                self.velocity = 0
                self.stepScore += rewardHitWall

                #this is because of a bug where the car does not move, reset the car
                self.hitWallBug += 1
                if self.hitWallBug > wallHitsUntilCarBreaks:
                    self.stepScore += rewardTotaledCar
                    self.resetWithAnotherPosition()
                    self.hitWallBug = 0
                return True
        
        return False
    
    #checks if the car hits a wall
    def hitAllWalls(self):
        for wall in self.walls:
            if self.hitWall(wall):
                return True
        self.hitWallBug = 0
        return False

    #checks if the car hits another car
    def hitAllCars(self):
        #check if it hits another car
        for i in range(len(self.allCars)):
            if i == self.ownIndex:
                continue
            if self.polygon.intersects(self.allCars[i].polygon):
                self.allCars[i].wasHit = True
                    
                #here we compute the reward
                #if it hits target
                if i == self.targetIndex:
                    self.allCars[i].wasHitByHunter = True
                    self.stepScore += rewardHitTarget
                #if it hits own hunter
                elif self.ownIndex == self.allCars[i].targetIndex:
                    self.allCars[i].wasHitByTarget = True
                    self.stepScore += rewardWasHitByHunter
                #if it hits bystander
                else:
                    self.stepScore += rewardHitCar
                
                self.resetWithAnotherPosition()
                return True
        return False

    #this should be the first function called in step
    def wasHitBeforeStep(self):
        self.stepScore = 0
        if not self.wasHit:
            return
        
        if self.wasHitByTarget:
            self.stepScore += rewardHitTarget
        elif self.wasHitByHunter:
            self.stepScore += rewardWasHitByHunter
        else:
            self.stepScore += rewardWasHitByCar

        self.wasHit = False
        self.wasHitByTarget = False
        self.wasHitByHunter = False
        self.resetWithAnotherPosition()
        
            






    #here we get what the car sees
    #we create rays that show us the car sight
    def getAllDistances(self):
        self.visionDistances = []
        self.lineCollisionPoints = []
        self.lineCollisionPointsType = []
        #set side vectors
        sightAngles = [0,20,45,75,105]
        self.getDistanceFromVector(carLength/2,0,0)
        for angle in sightAngles:
            self.getDistanceFromVector(carLength/2,carWidth/2,angle)
            self.getDistanceFromVector(carLength/2,-carWidth/2,-angle)
        self.getDistanceFromVector(-carLength/2,carWidth/2,180)
        self.getDistanceFromVector(-carLength/2,-carWidth/2,180)
        return [self.visionDistances,self.lineCollisionPointsType]



    #we find the coordinates of the ray then we find the closest point on the segment
    def getDistanceFromVector(self,x,y,angle):
        vectorOriginPoint = self.getPositionRelativeToRotationAngle(x,y)
        visionVectorDirection = self.direction.rotate(angle).normalize() * carVisionMaxRange
        closestPoint,smallestDistance = self.getClosestHitToWall(vectorOriginPoint,(vectorOriginPoint[0] + visionVectorDirection[0],vectorOriginPoint[1] + visionVectorDirection[1]))
        collisionType = wallType
        closestPointCar,smallestDistanceCar = self.getClosestHitToCar(vectorOriginPoint,(vectorOriginPoint[0] + visionVectorDirection[0],vectorOriginPoint[1] + visionVectorDirection[1]))

        if smallestDistanceCar < smallestDistance:
            closestPoint = closestPointCar
            smallestDistance = smallestDistanceCar
            collisionType = carType

        
        if closestPoint.x == 0 and closestPoint.y == 0:
            self.visionDistances.append(int(carVisionMaxRange))
        else:
            self.visionDistances.append(int(smallestDistance))

        self.lineCollisionPoints.append((vectorOriginPoint,(closestPoint.x,closestPoint.y)))
        self.lineCollisionPointsType.append(collisionType)
        


    #receives a position on the car
    #returns a vector with the position on the surface
    def getPositionRelativeToRotationAngle(self,x,y):
        directionVector = pygame.Vector2(self.direction).normalize()
        normalVector = self.direction.rotate(90).normalize()
        return pygame.Vector2(self.xCenter,self.yCenter) +((directionVector * x) + (normalVector * y))

    #given a line and the cars, find the intersection with the closest car
    #returns the point and the distance
    def getClosestHitToCar(self, point1, point2):
        closestCarSideHit = pygame.Vector2(0,0)
        minDistance = 2 * min(windowHeight, windowWidth)
        line1 = LineString([Point(point1),Point(point2)])

        for i in range(len(self.allCars)):
            if i == self.ownIndex:
                continue
            if not self.allCars[i].stillAlive:
                continue
            for ii in range(4):
                jj = (ii+1)%4
                line2Point1 = Point((self.allCars[i].corners[ii].x,self.allCars[i].corners[ii].y))
                line2Point2 = Point((self.allCars[i].corners[jj].x,self.allCars[i].corners[jj].y))
                line2 = LineString([line2Point1,line2Point2])
                collisionPoint = line1.intersection(line2)

                if collisionPoint.is_empty:
                    continue
                if isinstance(collisionPoint,LineString):
                    collisionPoint = line2Point1
                    if Point(point1).distance(line2Point2) < Point(point1).distance(line2Point1):
                        collisionPoint = line2Point2
                collisionPoint = (collisionPoint.x,collisionPoint.y)

                distanceToCar = distanceBetweenPoints(point1,collisionPoint)
                if distanceToCar < minDistance:
                    minDistance = distanceToCar
                    closestCarSideHit = Vector2(collisionPoint)
        return closestCarSideHit,minDistance

            
    #given a line and the walls, find the intersection with the closest wall
    #returns the point and the distance
    def getClosestHitToWall(self, point1, point2):
        closestWallHit = pygame.Vector2(0,0)
        minDistance = 2 * min(windowHeight, windowWidth)
        line1 = LineString([Point(point1),Point(point2)])

        for wall in self.walls:
            line2Point1 = Point(wall.points[0])
            line2Point2 = Point(wall.points[1])
            line2 = LineString([line2Point1,line2Point2])
            collisionPoint = line1.intersection(line2)
            
            if collisionPoint.is_empty:
                continue
            if isinstance(collisionPoint,LineString):
                    collisionPoint = line2Point1
                    if Point(point1).distance(line2Point2) < Point(point1).distance(line2Point1):
                        collisionPoint = line2Point2
            collisionPoint = (collisionPoint.x,collisionPoint.y)
            

            distanceToWall = distanceBetweenPoints(point1,collisionPoint)
            if distanceToWall < minDistance:
                minDistance = distanceToWall
                closestWallHit = Vector2(collisionPoint)
        return closestWallHit,minDistance

    def scoreSeeTarget(self):
        if abs(self.angleToTarget) < 106 and abs(self.angleToTarget) < abs(self.previousAngleToTarget):
            self.stepScore += (106 - abs(self.angleToTarget)) / 10
            if self.velocity == 0:
                self.stepScore += rewardDoesNotMoveWhenItSeesTarget
        if self.distanceToTarget < carVisionMaxRange and self.distanceToTarget <  self.previousDistanceToTarget:
            self.stepScore += (carVisionMaxRange - self.distanceToTarget) / 5
        
        distanceBetweenCarAndTarget = distanceBetweenPoints((self.xCenter, self.yCenter), (self.allCars[self.targetIndex].xCenter,self.allCars[self.targetIndex].yCenter))
        if distanceBetweenCarAndTarget < self.distanceBetweenHunterAndTarget:
            self.stepScore += 2
            self.distanceBetweenHunterAndTarget = distanceBetweenCarAndTarget
        
        self.stepScore = int(self.stepScore)


    #checks if it can see the target car
    #returns the angle it sees it at and the distance
    #if it cannot see it returns 106 and 0
    def seeTarget(self):
        carCenterPoint = (self.xCenter,self.yCenter)
        #make a list of the center and all 4 corners of the target car
        targetPoints = [(self.allCars[self.targetIndex].xCenter,self.allCars[self.targetIndex].yCenter)]
        for corner in self.allCars[self.targetIndex].corners:
            targetPoints.append((corner.x,corner.y))

        targetPointFiltered = []
        self.previousAngleToTarget = self.angleToTarget

        #find the angle between the direction vector and the given point
        #if the angle is smaller than 105 then save the point
        for i in range(len(targetPoints)):
            xDiff = targetPoints[i][0] - self.xCenter 
            yDiff = targetPoints[i][1] - self.yCenter
            if xDiff == 0  and yDiff == 0:
                continue
            toTargetVector = Vector2(xDiff, yDiff).normalize()
            self.angleToTarget = self.direction.angle_to(toTargetVector)
            if abs(self.angleToTarget) <= 105 and distanceBetweenPoints(carCenterPoint,targetPoints[i]) < carVisionMaxRange:
                targetPointFiltered.append(targetPoints[i])

        #target is outside sight range, so it cannot be seen
        if not targetPointFiltered:
            self.angleToTarget = 106
            return 106,0

        targetPoints = targetPointFiltered
        targetPointFiltered = []
        
        #now we check if target is blocked by walls
        for targetPoint in targetPoints:
            targetCanBeSeen = True
            for wall in self.walls:
                if linesIntersect(carCenterPoint,targetPoint,wall.points[0],wall.points[1]):
                    targetCanBeSeen = False
                    break
            if targetCanBeSeen:
                #check if target is blocked by cars
                for i in range(len(self.allCars)):
                    if i == self.ownIndex or i == self.targetIndex:
                        continue
                    for ii in range(4):
                        jj = (ii+1)%4
                        if linesIntersect(carCenterPoint,targetPoint,(self.allCars[i].corners[ii].x,self.allCars[i].corners[ii].y),(self.allCars[i].corners[jj].x,self.allCars[i].corners[jj].y)):
                            targetCanBeSeen = False
                            break
                    if not targetCanBeSeen:
                        break
            if targetCanBeSeen:
                targetPointFiltered.append(targetPoint)
        
        if not targetPointFiltered:
            self.angleToTarget = 106
            return 106,0
        if len(targetPointFiltered) > 1:
            targetPoint = tuple(map(mean,zip(*targetPointFiltered)))
        else:
            targetPoint = targetPointFiltered[0]

        toTargetVector = Vector2(targetPoint[0] - self.xCenter , targetPoint[1] - self.yCenter).normalize()
        self.angleToTarget = self.direction.angle_to(toTargetVector)

        self.previousDistanceToTarget = self.distanceToTarget
        self.distanceToTarget = distanceBetweenPoints(carCenterPoint,targetPoint)
        if self.distanceToTarget > carVisionMaxRange:
            self.distanceToTarget = carVisionMaxRange
        return int(self.angleToTarget), int(self.distanceToTarget)
                

        
            
import math

from pygame import Vector2

gameTime = 90000

#colors
color_black = (0,0,0)
color_white = (255,255,255)
color_red = (255,0,0)
color_green = (0,128,0)
color_blue = (0,0,255)

carMaxLives = 5

#renderSizes
carLength = 50
carWidth = 25
windowWidth = 1300
windowHeight = 700

#car driving
carMaxSpeed = 10
carMaxSpeedReverse = -4
carForwardAcceleration = 3
carBreak = 6
carReverseAcceleration = 1
turningAngle = 5
friction = 0.95
driftFriction = 0.1


#observable information
wallType = 0
carType = 1
carVisionMaxRange = 400

#reward 
rewardHitCar = -100
rewardWasHitByCar = -50
rewardHitTarget = 10000
rewardHitWall = -1
rewardHitsHunter = -500
rewardWasHitByHunter = -200
rewardSeesTarget = 1
rewardTotaledCar = -50
wallHitsUntilCarBreaks = 10


def radiansToAngle(radians):
    return radians * 180 / math.pi

def angleToRadians(angle):
    return angle * math.pi / 180

def vectorToAngle(vector):
    if vector.length() == 0:
        return 0
    return math.degrees(math.atan2(vector.y, vector.x))


def onSegment(p, q, r):
    if ( (q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and
           (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
        return True
    return False

def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Collinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise
    val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1]))
    if (val > 0):
         
        # Clockwise orientation
        return 1
    elif (val < 0):
         
        # Counterclockwise orientation
        return 2
    else:
         
        # Collinear orientation
        return 0

def linesIntersect(Line1Point1,Line1Point2,Line2Point1,Line2Point2):
    #receive them as tuples of 2
     # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(Line1Point1, Line1Point2, Line2Point1)
    o2 = orientation(Line1Point1, Line1Point2, Line2Point2)
    o3 = orientation(Line2Point1, Line2Point2, Line1Point1)
    o4 = orientation(Line2Point1, Line2Point2, Line1Point2)
 
    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True
 
    # Special Cases
 
    # Line1Point1 , Line1Point2 and Line2Point1 are collinear and Line2Point1 lies on segment p1q1
    if ((o1 == 0) and onSegment(Line1Point1, Line2Point1, Line1Point2)):
        return True
 
    # Line1Point1 , Line1Point2 and Line2Point2 are collinear and Line2Point2 lies on segment p1q1
    if ((o2 == 0) and onSegment(Line1Point1, Line2Point2, Line1Point2)):
        return True
 
    # Line2Point1 , Line2Point2 and Line1Point1 are collinear and Line1Point1 lies on segment p2q2
    if ((o3 == 0) and onSegment(Line2Point1, Line1Point1, Line2Point2)):
        return True
 
    # Line2Point1 , Line2Point2 and Line1Point2 are collinear and Line1Point2 lies on segment p2q2
    if ((o4 == 0) and onSegment(Line2Point1, Line1Point2, Line2Point2)):
        return True
 
    # If none of the cases
    return False


def lineIntersectionPoint(Line1Point1,Line1Point2,Line2Point1,Line2Point2):
    d = (Line2Point2[1] - Line2Point1[1]) * (Line1Point2[0] - Line1Point1[0]) - (Line2Point2[0] - Line2Point1[0]) * (Line1Point2[1] - Line1Point1[1])
    if d:
        uA = ((Line2Point2[0] - Line2Point1[0]) * (Line1Point1[1] - Line2Point1[1]) - (Line2Point2[1] - Line2Point1[1]) * (Line1Point1[0] - Line2Point1[0])) / d
        uB = ((Line1Point2[0] - Line1Point1[0]) * (Line1Point1[1] - Line2Point1[1]) - (Line1Point2[1] - Line1Point1[1]) * (Line1Point1[0] - Line2Point1[0])) / d

    d = (Line2Point2[1] - Line2Point1[1]) * (Line1Point2[0] - Line1Point1[0]) - (Line2Point2[0] - Line2Point1[0]) * (Line1Point2[1] - Line1Point1[1])
    if d:
        uA = ((Line2Point2[0] - Line2Point1[0]) * (Line1Point1[1] - Line2Point1[1]) - (Line2Point2[1] - Line2Point1[1]) * (Line1Point1[0] - Line2Point1[0])) / d
        uB = ((Line1Point2[0] - Line1Point1[0]) * (Line1Point1[1] - Line2Point1[1]) - (Line1Point2[1] - Line1Point1[1]) * (Line1Point1[0] - Line2Point1[0])) / d
    else:
        return
    if not(0 <= uA <= 1 and 0 <= uB <= 1):
        return
    x = Line1Point1[0] + uA * (Line1Point2[0] - Line1Point1[0])
    y = Line1Point1[1] + uA * (Line1Point2[1] - Line1Point1[1])
 
    return x, y

def distanceBetweenPoints(point1,point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
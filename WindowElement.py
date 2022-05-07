import re
from shapely.geometry import Polygon

class WindowElement:
    def __init__(self):
        #the points should be given in an order such that if a polygon is created it is convex
        self.points = []

    def getAllPointsCoordinates(self):
        pointCoordinates = []
        for point in self.points:
            pointCoordinates.append(point.getCoordinates())
        return pointCoordinates

    def draw(self,window):
        pass

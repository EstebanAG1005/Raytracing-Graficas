from lib import *
from math import *


class Sphere(object):
    def __init__(self,center,radius,colores):
        self.center = center
        self.radius = radius
        self.colores = colores

    def ray_intersect(self, origin, direction):
        L = sub(self.center, origin)
        tca = dot(L, direction)

        l = length(L)

        d2 = l**2 - tca**2  
        

        if d2 > self.radius**2:
            return False

        thc = (self.radius**2 - d2)**1/2

        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return False

        return True
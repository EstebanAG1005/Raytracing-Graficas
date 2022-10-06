from lib import *
from math import *
from sphere import *
from material import *

class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clear_color = color(0,0,0)
        self.current_color = color(255,255,255)
        self.clear()
        self.scene = []
        self.background_color = color(0, 0, 0)

    def clear(self):
        self.framebuffer = [
            [self.clear_color for x in range(self.width)]
            for y in range(self.height)
        ]

    def point(self,x,y,c=None):
        if y >= 0 and y < self.height and x >= 0 and x < self.width:
            self.framebuffer[y][x] = c or self.current_color
    
    def write(self, filename):
        write(filename, self.width, self.height, self.framebuffer)

    def render(self):
        fov = int(pi/2)
        ar = self.width/self.height
        tana = tan(fov/2)
        
        for y in range(self.height):
            for x in range(self.width):
                i = ((2 * (x + 0.5) / self.width) -1) * ar * tana
                j = (1 - (2 * (y + 0.5) / self.height))* tana
                
                direction = norm(V3(i,j,-1))
                self.framebuffer[y][x] = self.cast_ray(V3(0,0,0), direction)
                

    def cast_ray(self,origin,direction):
        material = self.scene_intersect(origin, direction)
        if material:
            return material.diffuse
        else:
            return self.background_color

    def scene_intersect(self,origin,direction):
        for s in self.scene:
            if s.ray_intersect(origin, direction):
                return s.material
        return None


# ----------------------- Main para correr --------------------------------

# ------------------ Colores ----------------------

ivory = Material(diffuse=color(100, 100, 80))
rubber = Material(diffuse=color(80, 10, 0))
snow = Material(diffuse=color(222, 231, 236))
button = Material(diffuse=color(0, 0, 0))
eye = Material(diffuse=color(250, 250, 250))
carrot = Material(diffuse=color(255, 165, 0))

r = Raytracer(800, 600)
r.scene = [
    Sphere(V3(-0.6, -2.1,-10), 0.1, button),
    Sphere(V3(-0.2, -1.9,-10), 0.1, button),
    Sphere(V3(0.2, -1.9,-10), 0.1, button),
    Sphere(V3(0.6, -2.1,-10), 0.1, button),

    Sphere(V3(0, -2.5,-10), 0.3, carrot),

    Sphere(V3(0.5, -3,-10), 0.1, button),
    Sphere(V3(-0.5, -3,-10), 0.1, button),
    Sphere(V3(0.5, -3,-10), 0.2, eye),
    Sphere(V3(-0.5, -3,-10), 0.2, eye),

    Sphere(V3(0, -0.4,-10), 0.3, button),
    Sphere(V3(0, 1,-10), 0.4, button),
    Sphere(V3(0, 3,-10), 0.5, button),
    Sphere(V3(0, -2.5,-10), 1.3, snow),
    Sphere(V3(0, 0,-10), 1.8, snow),
    Sphere(V3(0, 3,-12), 2.8, snow)
]
r.point(100, 100)

r.render()

r.write('RT1.bmp')
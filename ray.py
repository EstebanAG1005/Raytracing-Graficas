from lib import *
from math import *
from sphere import *
from material import *
from light import *


class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clear_color = color(0,0,0)
        self.current_color = color(255,255,255)
        self.clear()
        self.scene = []
        self.background_color = color(0, 0, 0)
        self.light = Light(V3(0,0,0),1)

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
                origin = V3(0,0,0)
                c = self.cast_ray(origin, direction)

                self.point(x, y, c)

    def cast_ray(self,origin,direction):

        
        material, intersect = self.scene_intersect(origin, direction)

        if intersect is None:
            return self.background_color

        if material is None:
            return self.background_color
            

        light_dir = norm(sub(self.light.position, intersect.point))
        intensity = dot(light_dir, intersect.normal)

       
        diffuse = color(
            int(material.diffuse[2] * intensity),
            int(material.diffuse[1] * intensity),
            int(material.diffuse[0] * intensity))

        return material.diffuse * intensity


    def scene_intersect(self,origin,direction):
        zbuffer = 999999
        material = None
        intersect = None

        for s in self.scene:
            object_intersect = s.ray_intersect(origin,direction)
            if object_intersect:
                if object_intersect.distance < zbuffer:
                    zbuffer = object_intersect.distance
                    material = s.colores
                    intersect = object_intersect
                return s.colores, intersect



# ----------------------- Main para correr --------------------------------


red = Material(diffuse=color(255,0,0))
white = Material(diffuse=color(255,255,255))


r = Raytracer(800, 600)
r.light = Light(V3(-3,-2,0), 1)
r.scene = [
    Sphere(V3(0, 3, -16), 2, white),
    Sphere(V3(0, 2.5, -10), 1, red),
    Sphere(V3(0, 0.2, -16), 1.5, white),
    
]

r.render()

r.write('r.bmp')
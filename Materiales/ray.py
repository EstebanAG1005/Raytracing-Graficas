from lib import *
from math import *
from sphere import *
from material import *
from light import *
from intersect import *
import random


class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clear_color = color(0, 0, 0)
        self.current_color = color(255, 255, 255)
        self.clear()
        self.scene = []
        self.background_color = color(0, 0, 0)
        self.light = Light(V3(0, 0, 0), 1)

    def clear(self):
        self.framebuffer = [
            [self.clear_color for x in range(self.width)] for y in range(self.height)
        ]

    def point(self, x, y, c=None):
        if y >= 0 and y < self.height and x >= 0 and x < self.width:
            self.framebuffer[y][x] = c or self.current_color

    def write(self, filename):
        write(filename, self.width, self.height, self.framebuffer)

    def render(self):
        fov = int(pi / 2)
        ar = self.width / self.height
        tana = tan(fov / 2)

        for y in range(self.height):
            for x in range(self.width):
                i = ((2 * (x + 0.5) / self.width) - 1) * ar * tana
                j = ((2 * (y + 0.5) / self.height) - 1) * tana

                direction = norm(V3(i, j, -1))
                self.framebuffer[y][x] = self.cast_ray(V3(0, 0, 0), direction)

    def cast_ray(self, origin, direction):

        material, intersect = self.scene_intersect(origin, direction)

        if intersect is None:
            return self.background_color

        if material is None:
            return self.background_color

        light_dir = norm(sub(self.light.position, intersect.point))
        intensity = dot(light_dir, intersect.normal)

        light_reflection = reflect(light_dir, intersect.normal)
        specular_intensity = self.light.intensity * (
            max(0, -dot(light_reflection, direction)) ** material.spec
        )

        diffuse = material.diffuse * intensity * material.albedo[0]
        specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
        return diffuse + specular

    def scene_intersect(self, origin, direction):
        zbuffer = 999999
        material = None
        intersect = None

        for s in self.scene:
            object_intersect = s.ray_intersect(origin, direction)
            if object_intersect:
                if object_intersect.distance < zbuffer:
                    zbuffer = object_intersect.distance
                    material = s.material
                    intersect = object_intersect

        return material, intersect


# ----------------------- Main para correr --------------------------------


rubber = Material(diffuse=color(80, 0, 0), albedo=(0.6, 0.3), spec=50)
ivory = Material(diffuse=color(100, 100, 80), albedo=(0.9, 0.1), spec=10)
cafe = Material(diffuse=color(170, 80, 40), albedo=(0.9, 0.3), spec=7)
cafe_claro = Material(diffuse=color(230, 170, 135), albedo=(0.9, 0.9), spec=35)
negro = Material(diffuse=color(0, 0, 0), albedo=(0.3, 0.3), spec=3)
lightGreen = Material(diffuse=color(130, 223, 36), albedo=(0.9, 0.9), spec=10)
iron = Material(diffuse=color(200, 200, 200), albedo=(1, 1), spec=20)
snow = Material(diffuse=color(250, 250, 250), albedo=(0.9, 0.9), spec=35)
gold = Material(diffuse=color(255, 215, 0), albedo=(0.9, 0.9), spec=35)
red = Material(diffuse=color(255, 0, 0), albedo=(0.9, 0.9), spec=35)
plata = Material(diffuse=color(192, 192, 192), albedo=(0.9, 0.9), spec=35)

r = Raytracer(800, 600)
r.light = Light(V3(-20, 0, 20), 1)
r.scene = [
    # OSO CAFE (derecha)
    # cuerpo y adorno
    Sphere(V3(2.5, -1, -10), 1.5, red),
    Sphere(V3(2.2, 0.2, -8.6), 0.2, lightGreen),
    Sphere(V3(1.8, 0.2, -8.6), 0.17, lightGreen),
    Sphere(V3(2.5, 0.2, -8.6), 0.17, lightGreen),
    Sphere(V3(2.8, 0.2, -8.6), 0.17, lightGreen),
    Sphere(V3(1.5, 0.2, -8.6), 0.17, lightGreen),
    # Listones dorador
    Sphere(V3(1.6, -0.2, -8.6), 0.17, gold),
    Sphere(V3(1.3, -0.2, -8.6), 0.17, gold),
    # Listones dorador
    Sphere(V3(1.9, -0.4, -8.6), 0.17, gold),
    Sphere(V3(1.6, -0.4, -8.6), 0.17, gold),
    # Listones dorador
    Sphere(V3(2.2, -0.6, -8.6), 0.17, gold),
    Sphere(V3(1.9, -0.6, -8.6), 0.17, gold),
    # Cuarta parte
    Sphere(V3(2.5, -0.8, -8.6), 0.17, gold),
    Sphere(V3(2.2, -0.8, -8.6), 0.17, gold),
    # Quinta parte
    Sphere(V3(2.8, -1, -8.6), 0.17, gold),
    Sphere(V3(2.5, -1, -8.6), 0.17, gold),
    # Sexta parte
    Sphere(V3(3.1, -1.2, -8.6), 0.17, gold),
    Sphere(V3(2.8, -1.2, -8.6), 0.17, gold),
    # cabeza
    Sphere(V3(2.5, 1.5, -10), 1.25, cafe_claro),
    # osico y orejas
    Sphere(V3(2.3, 1.1, -9), 0.4, cafe),
    Sphere(V3(3.4, 2.3, -9), 0.35, cafe),
    Sphere(V3(1.4, 2.3, -9), 0.35, cafe),
    # extremidades
    Sphere(V3(4, 0, -10), 0.45, cafe_claro),
    Sphere(V3(1, 0, -10), 0.45, cafe_claro),
    Sphere(V3(4, -2.2, -10), 0.5, cafe_claro),
    Sphere(V3(1, -2.2, -10), 0.5, cafe_claro),
    # nariz y ojos
    Sphere(V3(2, 1, -8), 0.1, negro),
    Sphere(V3(2.3, 1.5, -8), 0.1, negro),
    Sphere(V3(1.7, 1.5, -8), 0.1, negro),
    # OSO BLANCO (izquierda)
    # cuerpo y adorno
    Sphere(V3(-2.5, -1, -10), 1.5, snow),
    Sphere(V3(-2.2, 0.2, -8.6), 0.2, red),
    Sphere(V3(-1.9, 0.2, -8.6), 0.17, red),
    Sphere(V3(-2.5, 0.2, -8.6), 0.17, red),
    Sphere(V3(-2.8, 0.2, -8.6), 0.17, red),
    # Cintas Plateadas
    Sphere(V3(-2.2, -0.2, -8.6), 0.2, plata),
    Sphere(V3(-1.9, -0.2, -8.6), 0.17, plata),
    Sphere(V3(-2.5, -0.2, -8.6), 0.17, plata),
    Sphere(V3(-2.8, -0.2, -8.6), 0.17, plata),
    Sphere(V3(-3.1, -0.2, -8.6), 0.17, plata),
    Sphere(V3(-1.6, -0.2, -8.6), 0.17, plata),
    # Cintas Plateadas
    Sphere(V3(-2.2, -0.8, -8.6), 0.2, plata),
    Sphere(V3(-1.9, -0.8, -8.6), 0.17, plata),
    Sphere(V3(-2.5, -0.8, -8.6), 0.17, plata),
    Sphere(V3(-2.8, -0.8, -8.6), 0.17, plata),
    Sphere(V3(-3.1, -0.8, -8.6), 0.17, plata),
    Sphere(V3(-1.6, -0.8, -8.6), 0.17, plata),
    Sphere(V3(-3.4, -0.8, -8.6), 0.17, plata),
    Sphere(V3(-1.3, -0.8, -8.6), 0.17, plata),
    # Cintas Plateadas
    Sphere(V3(-2.2, -1.6, -8.6), 0.2, plata),
    Sphere(V3(-1.9, -1.6, -8.6), 0.17, plata),
    Sphere(V3(-2.5, -1.6, -8.6), 0.17, plata),
    Sphere(V3(-2.8, -1.6, -8.6), 0.17, plata),
    Sphere(V3(-3.1, -1.6, -8.6), 0.17, plata),
    Sphere(V3(-1.6, -1.6, -8.6), 0.17, plata),
    # cabeza
    Sphere(V3(-2.5, 1.5, -10), 1.25, snow),
    # osico y orejas
    Sphere(V3(-2.4, 1.1, -9), 0.4, snow),
    Sphere(V3(-3.3, 2.3, -9), 0.35, snow),
    Sphere(V3(-1.3, 2.3, -9), 0.35, snow),
    # extremidades
    Sphere(V3(-4, 0, -10), 0.45, snow),
    Sphere(V3(-1, 0, -10), 0.45, snow),
    Sphere(V3(-4, -2.2, -10), 0.5, snow),
    Sphere(V3(-1, -2.2, -10), 0.5, snow),
    # nariz y ojos
    Sphere(V3(-2.1, 1, -8), 0.1, negro),
    Sphere(V3(-2.4, 1.5, -8), 0.1, negro),
    Sphere(V3(-1.8, 1.5, -8), 0.1, negro),
]

r.render()

r.write("RT2.bmp")

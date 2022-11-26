from lib import *
from math import *
from sphere import *
from material import *
from light import *
from intersect import *
import random
from Plane import *

MAX_RECURSION_DEPTH = 3


class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clear_color = color(0, 0, 0)
        self.current_color = color(255, 255, 255)
        self.clear()
        self.scene = []
        self.background_color = color(50, 50, 200)
        self.light = Light(V3(0, 0, 0), 1)
        self.envmap = None

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

    def cast_ray(self, origin, direction, recursion=0):

        material, intersect = self.scene_intersect(origin, direction)

        if (
            material is None or recursion >= MAX_RECURSION_DEPTH
        ):  # break recursion of reflections after n iterations
            if self.envmap:
                return self.envmap.get_color(direction)
            return self.background_color

        if intersect is None:
            return self.background_color

        offset_normal = multi(intersect.normal, 1.1)  # avoids intercept with itself
        # Reflection

        if material.albedo[2] > 0:
            reverse_direction = multi(direction, -1)
            reflect_direction = reflect(direction, intersect.normal)
            reflect_orig = (
                sub(intersect.point, offset_normal)
                if dot(reflect_direction, intersect.normal) < 0
                else suma(intersect.point, offset_normal)
            )
            reflect_color = self.cast_ray(
                reflect_orig, reflect_direction, recursion + 1
            )
        else:
            reflect_color = color(0, 0, 0)

        if material.albedo[3] > 0:
            refract_dir = refract(
                direction, intersect.normal, material.refractive_index
            )
            refract_orig = (
                sub(intersect.point, offset_normal)
                if dot(refract_dir, intersect.normal) < 0
                else suma(intersect.point, offset_normal)
            )
            refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
        else:
            refract_color = color(0, 0, 0)

        # Shadow

        light_dir = norm(sub(self.light.position, intersect.point))
        intensity = dot(light_dir, intersect.normal)

        light_distance = length(sub(self.light.position, intersect.point))

        light_reflection = reflect(light_dir, intersect.normal)
        specular_intensity = self.light.intensity * (
            max(0, -dot(light_reflection, direction)) ** material.spec
        )

        diffuse = material.diffuse * intensity * material.albedo[0]
        specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
        reflection = reflect_color * material.albedo[2]
        refraction = refract_color * material.albedo[3]

        shadow_orig = (
            sub(intersect.point, offset_normal)
            if dot(light_dir, intersect.normal) < 0
            else suma(intersect.point, offset_normal)
        )
        shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
        shadow_intensity = 0

        if (
            shadow_material
            and length(sub(shadow_intersect.point, shadow_orig)) < light_distance
        ):
            shadow_intensity = 0.9

        intensity = (
            self.light.intensity
            * max(0, dot(light_dir, intersect.normal))
            * (1 - shadow_intensity)
        )

        if material.texture and intersect.text_coords is not None:
            text_color = material.texture.get_color(
                intersect.text_coords[0], intersect.text_coords[1]
            )
            diffuse = text_color * 255

        return diffuse + specular + reflection + refraction

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


# rubber = Material(diffuse=color(80,0,0), albedo=(0.6,  0.3), spec=50)
# ivory = Material(diffuse=color(100,100,80), albedo=(0.9,  0.1), spec=10)
coffee = Material(diffuse=color(71, 51, 10), albedo=(0.6, 0.3, 0, 0, 0), spec=10)
softcoffee = Material(diffuse=color(230, 170, 135), albedo=(0.9, 0.9), spec=35)
dark = Material(diffuse=color(0, 0, 0), albedo=(0.3, 0.3), spec=3)
lightGreen = Material(diffuse=color(130, 223, 36), albedo=(0.9, 0.9), spec=10)
iron = Material(diffuse=color(200, 200, 200), albedo=(1, 1, 0, 0), spec=20)
cuarzo = Material(diffuse=color(250, 250, 250), albedo=(0.9, 0.9, 0, 0), spec=35)

ivory = Material(diffuse=color(100, 100, 80), albedo=(0.6, 0.3, 0.1, 0), spec=50)
rubber = Material(diffuse=color(80, 0, 0), albedo=(0.9, 0.1, 0, 0, 0), spec=10)
mirror = Material(diffuse=color(255, 255, 255), albedo=(0, 10, 0.8, 0), spec=1425)
awita = Material(
    diffuse=color(135, 206, 235),
    albedo=[0.9, 0.1, 0.3, 0.3],
    spec=1425,
    refractive_index=1.5,
)
grey = Material(diffuse=color(128, 128, 128), albedo=(0.3, 0.3, 0, 0), spec=3)
# cuarzo = Material(texture=('./mine_madera.bmp'))

madera = Material(texture=Texture("./maderamine.bmp"))
hojas = Material(texture=Texture("./hojas.bmp"))
glass_mine = Material(texture=Texture("./glass.bmp"))
cobblestone = Material(texture=Texture("./piedra2.bmp"))
door = Material(texture=Texture("./doormi.bmp"))

r = Raytracer(800, 600)
r.light = Light(V3(-20, 20, 20), 1)

r.envmap = Envmap("./lock.bmp")

r.scene = [
    # Techo principal hecho de cuarzo
    Cube(V3(1, 1, -9.25), 0.5, cuarzo),
    Cube(V3(0.5, 1, -9.25), 0.5, cuarzo),
    Cube(V3(0, 1, -9.25), 0.5, cuarzo),
    Cube(V3(-0.5, 1, -9.25), 0.5, cuarzo),
    Cube(V3(-1, 1, -9.25), 0.5, cuarzo),
    Cube(V3(-1.5, 1, -9.25), 0.5, cuarzo),
    Cube(V3(-2, 1, -9.25), 0.5, cuarzo),
    Cube(V3(-2.5, 1, -9.25), 0.5, cuarzo),
    Cube(V3(-3, 1, -9.25), 0.5, cuarzo),
    Cube(V3(-3.5, 1, -9.25), 0.5, cuarzo),
    Cube(V3(-4, 1, -9.25), 0.5, cuarzo),
    # Techo en Desnivel
    Cube(V3(1, 1, -9.25), 0.5, cuarzo),
    Cube(V3(1.5, 1, -9.25), 0.5, cuarzo),
    Cube(V3(1.5, 1.5, -9.25), 0.5, cuarzo),
    Cube(V3(2, 1.5, -9.25), 0.5, cuarzo),
    Cube(V3(2, 2, -9.25), 0.5, cuarzo),
    Cube(V3(2.5, 2, -9.25), 0.5, cuarzo),
    Cube(V3(2.5, 2.5, -9.25), 0.5, cuarzo),
    Cube(V3(3, 2.5, -9.25), 0.5, cuarzo),
    Cube(V3(3.5, 2.5, -9.25), 0.5, cuarzo),
    Cube(V3(4, 2.5, -9.25), 0.5, cuarzo),
    Cube(V3(4, 2, -9.25), 0.5, cuarzo),
    Cube(V3(4.5, 2, -9.25), 0.5, cuarzo),
    Cube(V3(4.5, 1.5, -9.25), 0.5, cuarzo),
    Cube(V3(5, 1.5, -9.25), 0.5, cuarzo),
    Cube(V3(5, 1, -9.25), 0.5, cuarzo),
    Cube(V3(5.5, 1, -9.25), 0.5, cuarzo),
    # #Columnas de madera izquierda
    Cube(V3(1.25, 1, -9.25), 0.25, madera),
    Cube(V3(1.25, 0.75, -9.25), 0.25, madera),
    Cube(V3(1.25, 0.50, -9.25), 0.25, madera),
    Cube(V3(1.25, 0.25, -9.25), 0.25, madera),
    Cube(V3(1.25, 0, -9.25), 0.25, madera),
    Cube(V3(1.25, -0.25, -9.25), 0.25, madera),
    Cube(V3(1.25, -0.50, -9.25), 0.25, madera),
    Cube(V3(1.25, -0.75, -9.25), 0.25, madera),
    Cube(V3(1.25, -1, -9.25), 0.25, madera),
    # # #columnas de madera derecha
    Cube(V3(5.25, 1.25, -9.25), 0.25, madera),
    Cube(V3(5.25, 1, -9.25), 0.25, madera),
    Cube(V3(5.25, 0.75, -9.25), 0.25, madera),
    Cube(V3(5.25, 0.50, -9.25), 0.25, madera),
    Cube(V3(5.25, 0.25, -9.25), 0.25, madera),
    Cube(V3(5.25, 0, -9.25), 0.25, madera),
    Cube(V3(5.25, -0.25, -9.25), 0.25, madera),
    Cube(V3(5.25, -0.50, -9.25), 0.25, madera),
    Cube(V3(5.25, -0.75, -9.25), 0.25, madera),
    Cube(V3(5.25, -1, -9.25), 0.25, madera),
    Cube(V3(5.25, -1.25, -9.25), 0.25, madera),
    Cube(V3(5.25, -1.5, -9.25), 0.25, madera),
    # Columna de madera medio
    Cube(V3(-1.5, 0.75, -9.25), 0.25, madera),
    Cube(V3(-1.5, 0.5, -9.25), 0.25, madera),
    Cube(V3(-1.5, 0.25, -9.25), 0.25, madera),
    Cube(V3(-1.5, 0, -9.25), 0.25, madera),
    Cube(V3(-1.5, -0.25, -9.25), 0.25, madera),
    Cube(V3(-1.5, -0.5, -9.25), 0.25, madera),
    Cube(V3(-1.5, -0.75, -9.25), 0.25, madera),
    Cube(V3(-1.5, -1, -9.25), 0.25, madera),
    # Columna de madera izquierda
    Cube(V3(-4, 0.75, -9.25), 0.25, madera),
    Cube(V3(-4, 0.5, -9.25), 0.25, madera),
    Cube(V3(-4, 0.25, -9.25), 0.25, madera),
    Cube(V3(-4, 0, -9.25), 0.25, madera),
    Cube(V3(-4, -0.25, -9.25), 0.25, madera),
    Cube(V3(-4, -0.5, -9.25), 0.25, madera),
    Cube(V3(-4, -0.75, -9.25), 0.25, madera),
    Cube(V3(-4, -1, -9.25), 0.25, madera),
    # Parte de Hojas
    Cube(V3(-1.5, -1.25, -9.25), 0.5, hojas),
    Cube(V3(-2, -1.25, -9.25), 0.5, hojas),
    Cube(V3(-2.5, -1.25, -9.25), 0.5, hojas),
    Cube(V3(-3, -1.25, -9.25), 0.5, hojas),
    Cube(V3(-3.5, -1.25, -9.25), 0.5, hojas),
    Cube(V3(-4, -1.25, -9.25), 0.5, hojas),
    # Gradas de madera
    Cube(V3(0, -1.40, -10), 0.5, madera),
    Cube(V3(-1, -1.40, -10), 0.5, madera),
    Cube(V3(-0.5, -1.40, -10), 0.5, madera),
    Cube(V3(-1.5, -1.40, -10), 0.5, madera),
    Cube(V3(0.5, -1.40, -10), 0.5, madera),
    Cube(V3(0.75, -1.40, -10), 0.5, madera),
    Cube(V3(0.85, -1.40, -10), 0.5, madera),
    # Parde abajo de columnas
    Cube(V3(1.35, -1.40, -10), 0.5, grey),
    Cube(V3(1.35, -0.85, -10), 0.5, grey),
    Cube(V3(1.35, -0.35, -10), 0.5, grey),
    Cube(V3(1.35, 0.15, -10), 0.5, grey),
    Cube(V3(1.35, 0.5, -10), 0.5, grey),
    # Parte de abajo columnas cobble
    Cube(V3(1.25, -1.25, -9.25), 0.5, cobblestone),
    Cube(V3(5.25, -1.30, -9.25), 0.5, cobblestone),
    Cube(V3(5.75, -1.30, -9.25), 0.5, hojas),
    # Porton de casa
    Cube(V3(1.75, -1.40, -10), 0.5, cuarzo),
    Cube(V3(2, -1.40, -10), 0.5, cuarzo),
    Cube(V3(2.5, -1.40, -10), 0.5, cuarzo),
    Cube(V3(3, -1.40, -10), 0.5, cuarzo),
    Cube(V3(3.5, -1.40, -10), 0.5, cuarzo),
    Cube(V3(4, -1.40, -10), 0.5, cuarzo),
    Cube(V3(4.5, -1.40, -10), 0.5, cuarzo),
    Cube(V3(5, -1.40, -10), 0.5, cuarzo),
    # Uno arriba porton
    Cube(V3(1.8, -0.90, -10), 0.5, cuarzo),
    Cube(V3(2, -0.90, -10), 0.5, cuarzo),
    Cube(V3(2.5, -0.90, -10), 0.5, cuarzo),
    Cube(V3(3, -0.90, -10), 0.5, cuarzo),
    Cube(V3(3.5, -0.90, -10), 0.5, cuarzo),
    Cube(V3(4, -0.90, -10), 0.5, cuarzo),
    Cube(V3(4.5, -0.90, -10), 0.5, cuarzo),
    Cube(V3(4.9, -0.90, -10), 0.5, cuarzo),
    # INTER arriba porton
    Cube(V3(1.75, -0.45, -10), 0.5, cuarzo),
    Cube(V3(2, -0.45, -10), 0.5, cuarzo),
    Cube(V3(2.5, -0.45, -10), 0.5, cuarzo),
    Cube(V3(3, -0.45, -10), 0.5, cuarzo),
    Cube(V3(3.5, -0.45, -10), 0.5, cuarzo),
    Cube(V3(4, -0.45, -10), 0.5, cuarzo),
    Cube(V3(4.5, -0.45, -10), 0.5, cuarzo),
    Cube(V3(4.9, -0.45, -10), 0.5, cuarzo),
    # dos arriba porton
    Cube(V3(1.75, -0.35, -10), 0.5, cuarzo),
    Cube(V3(2, -0.35, -10), 0.5, cuarzo),
    Cube(V3(2.5, -0.35, -10), 0.5, cuarzo),
    Cube(V3(3, -0.35, -10), 0.5, cuarzo),
    Cube(V3(3.5, -0.35, -10), 0.5, cuarzo),
    Cube(V3(4, -0.35, -10), 0.5, cuarzo),
    Cube(V3(4.5, -0.35, -10), 0.5, cuarzo),
    Cube(V3(4.9, -0.35, -10), 0.5, cuarzo),
    # tres arriba porton
    Cube(V3(1.75, 0.15, -10), 0.5, grey),
    Cube(V3(2, 0.15, -10), 0.5, grey),
    Cube(V3(2.5, 0.15, -10), 0.5, grey),
    Cube(V3(3, 0.15, -10), 0.5, grey),
    Cube(V3(3.5, 0.15, -10), 0.5, grey),
    Cube(V3(4, 0.15, -10), 0.5, grey),
    Cube(V3(4.5, 0.15, -10), 0.5, grey),
    Cube(V3(5, 0.15, -10), 0.5, grey),
    Cube(V3(5.5, 0.15, -10), 0.5, grey),
    Cube(V3(6, 0.15, -10), 0.5, grey),
    Cube(V3(6, -0.35, -10), 0.5, grey),
    Cube(V3(6, -0.85, -10), 0.5, grey),
    Cube(V3(6, -1.30, -10), 0.5, grey),
    # cuatro arriba porton
    Cube(V3(1.75, 0.65, -10), 0.5, grey),
    Cube(V3(2, 0.65, -10), 0.5, grey),
    Cube(V3(2.5, 0.65, -10), 0.5, grey),
    Cube(V3(3, 0.65, -10), 0.5, grey),
    Cube(V3(3.5, 0.65, -10), 0.5, grey),
    Cube(V3(4, 0.65, -10), 0.5, grey),
    Cube(V3(4.5, 0.65, -10), 0.5, grey),
    Cube(V3(5, 0.65, -10), 0.5, grey),
    Cube(V3(5.5, 0.65, -10), 0.5, grey),
    Cube(V3(6, 0.65, -10), 0.5, grey),
    # Arreglo derecha
    Cube(V3(5.5, 0.65, -10), 0.5, grey),
    Cube(V3(5.5, 0.15, -10), 0.5, grey),
    Cube(V3(5.5, -0.35, -10), 0.5, grey),
    Cube(V3(5.5, -0.45, -10), 0.5, grey),
    Cube(V3(5.5, -0.90, -10), 0.5, grey),
    Cube(V3(5.5, -1.40, -10), 0.5, grey),
    # cinco arriba porton
    Cube(V3(1.75, 1.15, -10), 0.5, grey),
    Cube(V3(2, 1.15, -10), 0.5, grey),
    Cube(V3(2.5, 1.15, -10), 0.5, grey),
    Cube(V3(3, 1.15, -10), 0.5, grey),
    Cube(V3(3.5, 1.15, -10), 0.5, grey),
    Cube(V3(4, 1.15, -10), 0.5, grey),
    Cube(V3(4.5, 1.15, -10), 0.5, grey),
    Cube(V3(5, 1.15, -10), 0.5, grey),
    Cube(V3(5.5, 1.15, -10), 0.5, grey),
    # seis arriba porton
    Cube(V3(2, 1.65, -10), 0.5, grey),
    Cube(V3(2.5, 1.65, -10), 0.5, grey),
    Cube(V3(3, 1.65, -10), 0.5, grey),
    Cube(V3(3.5, 1.65, -10), 0.5, grey),
    Cube(V3(4, 1.65, -10), 0.5, grey),
    Cube(V3(4.5, 1.65, -10), 0.5, grey),
    # siete arriba porton
    Cube(V3(2.5, 2.15, -10), 0.5, grey),
    Cube(V3(3, 2.15, -10), 0.5, grey),
    Cube(V3(3.5, 2.15, -10), 0.5, grey),
    Cube(V3(4, 2.15, -10), 0.5, grey),
    # botones
    Cube(V3(1.7, -0.90, -9.25), 0.25, iron),
    Cube(V3(2.7, -0.90, -9.25), 0.25, iron),
    Cube(V3(3.7, -0.90, -9.25), 0.25, iron),
    Cube(V3(4.7, -0.90, -9.25), 0.25, iron),
    # Segunda pared negra
    Cube(V3(0.85, -1.40, -10), 0.5, grey),
    Cube(V3(0.85, -0.85, -10), 0.5, grey),
    Cube(V3(0.85, -0.35, -10), 0.5, grey),
    Cube(V3(0.85, 0.15, -10), 0.5, grey),
    Cube(V3(0.85, 0.5, -10), 0.5, grey),
    Cube(V3(0.85, 0.75, -10), 0.5, grey),
    # Tecerda Pared
    Cube(V3(-1.5, -0.80, -9.5), 0.5, grey),
    Cube(V3(-1.5, -0.55, -9.5), 0.5, grey),
    Cube(V3(-1.5, -0.35, -9.5), 0.5, grey),
    Cube(V3(-1.5, 0.15, -9.5), 0.5, grey),
    Cube(V3(-1.5, 0.5, -9.5), 0.5, grey),
    Cube(V3(-1.25, -0.80, -9.5), 0.5, grey),
    Cube(V3(-1.25, -0.55, -9.5), 0.5, grey),
    Cube(V3(-1.25, -0.35, -9.5), 0.5, grey),
    Cube(V3(-1.25, 0.15, -9.5), 0.5, grey),
    Cube(V3(-1.25, 0.5, -9.5), 0.5, grey),
    # Puerta
    Cube(V3(-0.25, 0, -11), 2.5, door),
    # Vidrio
    Cube(V3(-2.75, 0, -10), 0.5, glass_mine),
    Cube(V3(-2.75, -0.25, -10), 0.5, glass_mine),
    Cube(V3(-3.25, 0, -10), 0.5, glass_mine),
    Cube(V3(-3.25, -0.25, -10), 0.5, glass_mine),
    Cube(V3(-3.75, -0.25, -10), 0.5, glass_mine),
    Cube(V3(-1.75, -0.25, -10), 0.5, glass_mine),
    Cube(V3(-1.25, -0.25, -10), 0.5, glass_mine),
    Cube(V3(-3.75, 0, -10), 0.5, glass_mine),
    Cube(V3(-2.25, 0, -10), 0.5, glass_mine),
    Cube(V3(-1.75, 0, -10), 0.5, glass_mine),
    Cube(V3(-1.25, 0, -10), 0.5, glass_mine),
    Cube(V3(-2.25, -0.25, -10), 0.5, glass_mine),
    Cube(V3(-3.75, 0.5, -10), 0.5, glass_mine),
    Cube(V3(-2.25, 0.5, -10), 0.5, glass_mine),
    Cube(V3(-3.25, 0.5, -10), 0.5, glass_mine),
    Cube(V3(-2.75, 0.5, -10), 0.5, glass_mine),
    Cube(V3(-1.75, 0.5, -10), 0.5, glass_mine),
    Cube(V3(-1.25, 0.5, -10), 0.5, glass_mine),
    # Cuarzo abajo
    Cube(V3(-1.5, -0.80, -10), 0.5, cuarzo),
    Cube(V3(-2, -0.80, -10), 0.5, cuarzo),
    Cube(V3(-2.5, -0.80, -10), 0.5, cuarzo),
    Cube(V3(-3, -0.80, -10), 0.5, cuarzo),
    Cube(V3(-3.5, -0.80, -10), 0.5, cuarzo),
    Cube(V3(-4, -0.80, -10), 0.5, cuarzo),
    # awita
    Cube(V3(-3, -5, -9.25), 4, awita),
    # Ventanita
    Cube(V3(3.2, 1.5, -9.25), 0.5, mirror),
    # Techo principal hecho de cuarzo
    Cube(V3(1, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(0.5, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(0, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(-0.5, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(-1, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(-1.5, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(-2, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(-2.5, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(-3, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(-3.5, 1.5, -9.25), 0.5, cobblestone),
    Cube(V3(-4, 1.5, -9.25), 0.5, cobblestone),
    # Techo principal hecho de cuarzo
    Cube(V3(2.5, 2.25, -10), 0.5, cobblestone),
    Cube(V3(2, 2.25, -10), 0.5, cobblestone),
    Cube(V3(1.5, 2.25, -10), 0.5, cobblestone),
    Cube(V3(1, 2.25, -10), 0.5, cobblestone),
    Cube(V3(0.5, 2.25, -10), 0.5, cobblestone),
    Cube(V3(0, 2.25, -10), 0.5, cobblestone),
    Cube(V3(-0.5, 2.25, -10), 0.5, cobblestone),
    Cube(V3(-1, 2.25, -10), 0.5, cobblestone),
    Cube(V3(-1.5, 2.25, -10), 0.5, cobblestone),
    Cube(V3(-2, 2.25, -10), 0.5, cobblestone),
    Cube(V3(-2.5, 2.25, -10), 0.5, cobblestone),
    Cube(V3(-3, 2.25, -10), 0.5, cobblestone),
    Cube(V3(-3.5, 2.25, -10), 0.5, cobblestone),
    Cube(V3(-4, 2.25, -10), 0.5, cobblestone),
    # Techo principal hecho de cuarzo
    Cube(V3(3.5, 3, -11), 0.5, cobblestone),
    Cube(V3(3, 3, -11), 0.5, cobblestone),
    Cube(V3(2.5, 3, -11), 0.5, cobblestone),
    Cube(V3(2, 3, -11), 0.5, cobblestone),
    Cube(V3(1.5, 3, -11), 0.5, cobblestone),
    Cube(V3(1, 3, -11), 0.5, cobblestone),
    Cube(V3(0.5, 3, -11), 0.5, cobblestone),
    Cube(V3(0, 3, -11), 0.5, cobblestone),
    Cube(V3(0.5, 3, -11), 0.5, cobblestone),
    Cube(V3(1, 3, -11), 0.5, cobblestone),
    Cube(V3(0.5, 3, -11), 0.5, cobblestone),
    Cube(V3(0, 3, -11), 0.5, cobblestone),
    Cube(V3(-0.5, 3, -11), 0.5, cobblestone),
    Cube(V3(-1, 3, -11), 0.5, cobblestone),
    Cube(V3(-1.5, 3, -11), 0.5, cobblestone),
    Cube(V3(-2, 3, -11), 0.5, cobblestone),
    Cube(V3(-2.5, 3, -11), 0.5, cobblestone),
    Cube(V3(-3, 3, -11), 0.5, cobblestone),
    Cube(V3(-3.5, 3, -11), 0.5, cobblestone),
    Cube(V3(-4, 3, -11), 0.5, cobblestone),
]

r.render()

# r.write("Final.bmp")
r.write("TEST.bmp")

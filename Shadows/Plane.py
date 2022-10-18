from lib import *
from sphere import *
from math import pi, acos, atan2
import struct

class Plane(object):
  def __init__(self, y, material):
    self.y = y
    self.material = material

  def ray_intersect(self, orig, direction):
    d = -(orig.y + self.y) / direction.y
    pt = suma(orig, multi(direction, d))

    if d <= 0 or abs(pt.x) > 2 or pt.z > -5 or pt.z < -10:
      return None

    normal = V3(0, 1, 0)

    return Intersect(
      distance=d,
      point=pt,
      normal=normal
    )

class Envmap(object):
  def __init__(self, path):
    self.path = path
    self.read()

  def read(self):
    image = open(self.path, 'rb')
    image.seek(10)
    header_size = struct.unpack('=l', image.read(4))[0]

    image.seek(14 + 4)
    self.width = struct.unpack('=l', image.read(4))[0]
    self.height = struct.unpack('=l', image.read(4))[0]
    image.seek(header_size)

    self.pixels = []
    for y in range(self.height):
      self.pixels.append([])
      for x in range(self.width):
        b = ord(image.read(1))
        g = ord(image.read(1))
        r = ord(image.read(1))
        self.pixels[y].append(color(r,g,b))

    image.close()

  def get_color(self, direction):
    direction = norm(direction)
    x = int( (atan2( direction[2], direction[0]) / (2 * pi) + 0.5) * self.width)
    y = int( acos(-direction[1]) / pi * self.height )

    if x < self.width and y < self.height:
      return self.pixels[y][x]

    return color(0, 0, 0)


class Cube(object):
  def __init__(self, position, size, material):
    self.position = position
    self.size = size
    self.material = material
    self.planes = []

    halfSize = size / 2
    #Se crean las 6 paredes del cubo con planos
    self.planes.append( Plane( sum(position, V3(halfSize,0,0)), V3(1,0,0), material))
    self.planes.append( Plane( sum(position, V3(-halfSize,0,0)), V3(-1,0,0), material))

    self.planes.append( Plane( sum(position, V3(0,halfSize,0)), V3(0,1,0), material))
    self.planes.append( Plane( sum(position, V3(0,-halfSize,0)), V3(0,-1,0), material))

    self.planes.append( Plane( sum(position, V3(0,0,halfSize)), V3(0,0,1), material))
    self.planes.append( Plane( sum(position, V3(0,0,-halfSize)), V3(0,0,-1), material))

  def ray_intersect(self, orig, direction):

    epsilon = 0.001
    #Se inicializan los values del boundingbox para el cubo
    minBounds = [0,0,0]
    maxBounds = [0,0,0]

    for i in range(3):
      minBounds[i] = self.position[i] - (epsilon + self.size / 2)
      maxBounds[i] = self.position[i] + (epsilon + self.size / 2)

    t = float('inf')
    intersect = None

    for plane in self.planes:
      planeInter = plane.ray_intersect(orig, direction)

      if planeInter is not None:
        if planeInter.point[0] >= minBounds[0] and planeInter.point[0] <= maxBounds[0]:
          if planeInter.point[1] >= minBounds[1] and planeInter.point[1] <= maxBounds[1]:
            if planeInter.point[2] >= minBounds[2] and planeInter.point[2] <= maxBounds[2]:
              if planeInter.distance < t:
                t = planeInter.distance
                intersect = planeInter

    if intersect is None:
      return None

    return Intersect(distance = intersect.distance,
                     point = intersect.point,
                     normal = intersect.normal)
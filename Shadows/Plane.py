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
        headerSize = struct.unpack('=l', image.read(4))[0]

        image.seek(14 + 4)
        self.width = struct.unpack('=l', image.read(4))[0]
        self.height = struct.unpack('=l', image.read(4))[0]
        image.seek(headerSize)

        self.framebuffer = []

        for y in range(self.height):
            self.framebuffer.append([])
            for x in range(self.width):
                b = ord(image.read(1))
                g = ord(image.read(1))
                r = ord(image.read(1))
                self.framebuffer[y].append(color(r,g,b))

        image.close()

    def getColor(self, direction):

        direction = norm(direction)

        x = int( (atan2( direction[2], direction[0]) / (2 * pi) + 0.5) * self.width)
        y = int( acos(-direction[1]) / pi * self.height )
        
        #print(x, y)
        if x < self.width and y < self.height:
            return self.framebuffer[y][x]
        else:
            return color(0, 0, 0)
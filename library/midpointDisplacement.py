#!/usr/bin/python
# Requirements:
#  - pyPNG @ http://pypng.googlecode.com

import math, random, sys
from numpy import *
from progressbar import ProgressBar, Percentage, ETA

class MDA():
    def __init__(self, width, height,roughness=8):
        self.size = width+height
        self.width = width
        self.height = height
        self.roughness = roughness
        self.heightmap = zeros((self.width,self.height))

    def run(self, globe=False, seaLevel=0.33):
        widgets = ['Generating heightmap: ', Percentage(), ' ', ETA() ]
        self.pbar = ProgressBar(widgets=widgets, maxval=self.width*self.height)
        self.heightmap = zeros((self.width,self.height))

        c1 = random.random()        # top
        c3 = random.random()        # bottom
        if globe: # try to create world that wraps around on a globe/sphere
            c2 = random.uniform(0.00, seaLevel)    # right
            c4 = random.uniform(0.00, seaLevel)    # left
        else:
            c2 = random.random()    # right
            c4 = random.random()    # left
        self.divideRect(0, 0, self.width, self.height, c1, c2, c3, c4)
        self.pbar.finish()
        del self.pbar

    def normalize(self, point): # +/- infinity are reset to 1 and 1 values
        if point < 0.0:
            point = 0.0
        elif point > 1.0:
            point = 1.0
        return point

    def displace(self, small_size):
        maxd = small_size / self.size * self.roughness
        return (random.random() - 0.5) * maxd

    def divideRect(self, x, y, width, height, c1, c2, c3, c4):
        self.pbar.update(x+y)
        new_width = math.floor(width / 2)
        new_height = math.floor(height / 2)

        if (width > 1 or height > 1):
            # average of all the points and normalize in case of "out of bounds" during displacement
            mid = self.normalize(self.normalize(((c1 + c2 + c3 + c4) / 4) + self.displace(new_width + new_height)))

            # midpoint of the edges is the average of its two endpoints
            edge1 = self.normalize((c1 + c2) / 2)
            edge2 = self.normalize((c2 + c3) / 2)
            edge3 = self.normalize((c3 + c4) / 2)
            edge4 = self.normalize((c4 + c1) / 2)

            # recursively go down the rabbit hole
            self.divideRect(x, y, new_width, new_height, c1, edge1, mid, edge4)
            self.divideRect(x + new_width, y, new_width, new_height, edge1, c2, edge2, mid)
            self.divideRect(x + new_width, y + new_height, new_width, new_height, mid, edge2, c3, edge3)
            self.divideRect(x, y + new_height, new_width, new_height, edge4, mid, edge3, c4)

        else:
            c = (c1 + c2 + c3 + c4) / 4

            x = int(x)
            y = int(y)

            self.heightmap[x][y] = c

            if (width == 2):
                self.heightmap[x + 1][y] = c
            if (height == 2):
                self.heightmap[x][y + 1] = c
            if (width == 2 and height == 2):
                self.heightmap[x + 1][y + 1] = c

# runs the program
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "You must pass a width, height, and roughness!"
        sys.exit()

    import png

    width = int(sys.argv[1])
    height = int(sys.argv[2])
    roughness = int(sys.argv[3])

    print "Setting things up..."
    mda = MDA(width, height, roughness)
    print "Thinking..."
    mda.run()
    print "done!"

#!/usr/bin/python
import math, random, sys
from numpy import *
from PySide import QtGui
from constants import *

class MDA():
    def __init__( self, width, height, roughness = 8 ):
        self.size = width + height
        self.width = width
        self.height = height
        self.roughness = roughness
        self.heightmap = zeros( ( self.width, self.height ) )

    def run( self, globe = False, seaLevel = 0.25, sb = None ):
        self.heightmap = zeros( ( self.width, self.height ) )
        self.sb = sb
        if self.sb != None:
            self.progressValue = 0
            self.progress = QtGui.QProgressBar()
            self.progress.setRange( 0, self.width * self.height )
            self.sb.addPermanentWidget( self.progress )

        if globe: # try to create world that wraps around on a globe/sphere
            c1 = random.uniform( 0.00, seaLevel )     # top
            c3 = random.uniform( 0.00, seaLevel )     # bottom
            c2 = random.uniform( 0.00, seaLevel )    # right
            c4 = random.uniform( 0.00, seaLevel )    # left
        else:
            c1 = random.random()    # top
            c3 = random.random()    # bottom
            c2 = random.random()    # right
            c4 = random.random()    # left
        self.divideRect( 0, 0, self.width, self.height, c1, c2, c3, c4 )

        if self.sb != None:
            self.sb.removeWidget( self.progress )
            del self.progress

    def normalize( self, point ): # +/- infinity are reset to 1 and 1 values
        if point < 0.0:
            point = 0.0
        elif point > 1.0:
            point = 1.0
        return point

    def displace( self, small_size ):
        maxd = small_size / self.size * self.roughness
        return ( random.random() - 0.5 ) * maxd

    def divideRect( self, x, y, width, height, c1, c2, c3, c4 ):
        new_width = math.floor( width / 2 )
        new_height = math.floor( height / 2 )

        if ( width > 1 or height > 1 ):
            # average of all the points and normalize in case of "out of bounds" during displacement
            mid = self.normalize( self.normalize( ( ( c1 + c2 + c3 + c4 ) / 4 ) + self.displace( new_width + new_height ) ) )

            # midpoint of the edges is the average of its two end points
            edge1 = self.normalize( ( c1 + c2 ) / 2 )
            edge2 = self.normalize( ( c2 + c3 ) / 2 )
            edge3 = self.normalize( ( c3 + c4 ) / 2 )
            edge4 = self.normalize( ( c4 + c1 ) / 2 )

            # recursively go down the rabbit hole
            self.divideRect( x, y, new_width, new_height, c1, edge1, mid, edge4 )
            self.divideRect( x + new_width, y, new_width, new_height, edge1, c2, edge2, mid )
            self.divideRect( x + new_width, y + new_height, new_width, new_height, mid, edge2, c3, edge3 )
            self.divideRect( x, y + new_height, new_width, new_height, edge4, mid, edge3, c4 )

        else:
            c = ( c1 + c2 + c3 + c4 ) / 4

            self.heightmap[x][y] = c

            if ( width == 2 ):
                self.heightmap[x + 1][y] = c
            if ( height == 2 ):
                self.heightmap[x][y + 1] = c
            if ( width == 2 and height == 2 ):
                self.heightmap[x + 1][y + 1] = c

        if self.sb != None:
            self.progress.setValue( self.progressValue )
            self.progressValue += 1

    def landMassPercent( self ):
        return self.heightmap.sum() / ( self.width * self.height )

    def averageElevation( self ):
        return average( self.heightmap )

    def hasNoMountains( self ):
        if self.heightmap.max() > BIOME_ELEVATION_MOUNTAIN:
            return False
        return True

    def landTouchesEastWest( self ):
        for x in range( 0, 1 ):
            for y in range( 0, self.height ):
                if self.heightmap[x, y] > WGEN_SEA_LEVEL or \
                    self.heightmap[self.width - 1 - x, y] > WGEN_SEA_LEVEL:
                    return True
        return False

    def landTouchesMapEdge( self ):
        result = False
        for x in range( 4, self.width - 4 ):
            if self.heightmap[x, 4] > WGEN_SEA_LEVEL or self.heightmap[x, self.height - 4] > WGEN_SEA_LEVEL:
                result = True
                break

        for y in range( 4, self.height - 4 ):
            if self.heightmap[4, y] > WGEN_SEA_LEVEL or self.heightmap[self.width - 4, y] > WGEN_SEA_LEVEL:
                result = True
                break

        return result

# runs the program
if __name__ == '__main__':
    if len( sys.argv ) != 4:
        print "You must pass a width, height, and roughness!"
        sys.exit()

    width = int( sys.argv[1] )
    height = int( sys.argv[2] )
    roughness = int( sys.argv[3] )

    print "Setting things up..."
    mda = MDA( width, height, roughness )
    print "Thinking..."
    import cProfile
    cProfile.run( 'mda.run()' )
    #mda.run()
    print "done!"

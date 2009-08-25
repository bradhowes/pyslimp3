#
# Copyright (C) 2009 Brad Howes.
#
# This file is part of Pyslimp3.
#
# Pyslimp3 is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3, or (at your option) any later version.
#
# Pyslimp3 is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Pyslimp3; see the file COPYING. If not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.
#

from random import randrange
from Content import *

#
# Base class for all screen savers. Defines the interface for Animator to use
# to update the display of an active screen saver. Derived classes must
# implement the updateDisplay() method.
#
class ScreenSaverBase( object ):

    def __init__( self, content ):

        #
        # Obtain a list of the individual characters from the original content.
        #
        self.original = map( lambda a: list( a ), content )
        
        #
        # Make a copy of the lists to serve as the new display.
        #
        self.display = self.original[ : ]

    #
    # Obtain a random character position as (X, Y) where X is a character
    # offset from [0-kDisplayWidth) and Y is a line number from
    # [0-kDisplayHeight)
    #
    def getRandomCharacterPosition( self ):
        value =randrange( kDisplayHeight * kDisplayWidth )
        y = value / kDisplayWidth
        x = value - y * kDisplayWidth
        return x, y

    #
    # Update the display, and return a list of N strings
    #
    def render( self ):
        self.updateDisplay()
        return map( lambda a: ''.join( a ), self.display )

    #
    # Update the screen saver display. Derived classes must define.
    #
    def updateDisplay( self ):
        raise NotImplementedError, 'updateDisplay'

#
# Screensaver that just shows a blank screen.
#
class Blanker( ScreenSaverBase ):

    kBlankLines = [ ' ' * kDisplayWidth ] * kDisplayHeight
    kName = 'Blank Display'

    def __init__( self, content ):
        ScreenSaverBase.__init__( self, self.kBlankLines )

    def updateDisplay( self ):
        return

#
# Screensaver that randomly replaces a character in the original screen with a
# blank one, or restores it if previously blanked.
#
class Zapper( ScreenSaverBase ):

    kName = 'Zap Characters'

    def updateDisplay( self ):
        x, y = self.getRandomCharacterPosition()
        if self.display[ y ][ x ] == ' ':
            self.display[ y ][ x ] = self.original[ y ][ x ]
        else:
            self.display[ y ][ x ] = ' '

#
# Screensaver that randomly swaps two characters.
#
class Swapper( ScreenSaverBase ):

    kName = 'Swap Characters'

    def updateDisplay( self ):
        x1, y1 = self.getRandomCharacterPosition()
        x2, y2 = self.getRandomCharacterPosition()
        value = self.display[ y1 ][ x1 ]
        self.display[ y1 ][ x1 ] = self.display[ y2 ][ x2 ]
        self.display[ y2 ][ x2 ] = value

#
# Screensaver that rotates left the original screen in an endless loop. Each
# line rotates faster than the line before it.
#
class LeftRotater( ScreenSaverBase ):

    kName = 'Rotate Left'

    def updateDisplay( self ):
        for index in range( kDisplayHeight ):
            line = self.display[ index ]
            self.display[ index ] = line[ index + 1 : ] + line[ : index + 1 ]

kScreenSavers = ( Blanker,
                  LeftRotater,
                  Swapper,
                  Zapper,
                  )

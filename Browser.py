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

from Display import iTunesSourceGenerator
from KeyProcessor import *

#
# Specialization of iTunesSourceGenerator that supports scrolling through a
# collection of objects. Derived classes must define getListing() to generate
# the line to show for the current object.
#
class Browser( iTunesSourceGenerator ):

    #
    # Characters to cycle through for a given digit (eg. pressing '2' three
    # times will leave a 'C' showing)
    #
    kDigits = [ '',
                '',
                'ABC',
                'DEF',
                'GHI', 
                'JKL',
                'MNO',
                'PQRS',
                'TUV',
                'WXYZ' ]

    def __init__( self, iTunes, prevLevel, collection ):
        iTunesSourceGenerator.__init__( self, iTunes )
        self.index = 0
        self.prevLevel = prevLevel
        self.collection = collection
        self.reset()

    def reset( self ):
        self.lastDigit = None
        self.digitIndex = 0

    #
    # Install handlers for the arrow keys.
    #
    def fillKeyMap( self ):
        iTunesSourceGenerator.fillKeyMap( self )
        self.addKeyMapEntry( kArrowUp, ( kModFirst, kModRepeat ), self.up )
        self.addKeyMapEntry( kArrowDown, ( kModFirst, kModRepeat ), self.down )
        self.addKeyMapEntry( kArrowLeft, ( kModFirst, ), self.left )
        self.addKeyMapEntry( kArrowRight,( kModFirst, ), self.right )

    def getMaxIndex( self ): return len( self.collection )

    def getCurrentObject( self ): return self.collection[ self.index ]

    def getIndexOverlay( self, prefix = '' ):
        if prefix: prefix += ' '
        return '%s%d/%d' % ( prefix, self.index + 1, self.getMaxIndex() )

    def generateWith( self, obj ):
        raise NotImplementedError, 'generateWith'

    def generate( self ):
        return self.generateWith( self.getCurrentObject() )

    #
    # Move to the previous item in the collection
    #
    def up( self ):
        index = self.index - 1
        if index == -1: index = self.getMaxIndex() - 1
        self.index = index
        self.reset()
        return self

    #
    # Move to the next item in the collection
    #
    def down( self ):
        index = self.index + 1
        if index == self.getMaxIndex(): index = 0
        self.index = index
        self.reset()
        return self

    #
    # Install the previous screen generator.
    #
    def left( self ): 
        self.reset()
        return self.prevLevel

    #
    # Does nothing. Derived classes may override.
    #
    def right( self ): return None

    def getNameAtIndex( self, index ):
        return self.collection[ index ].getName()

    #
    # Override of DisplayGenerator method. If there are 10 or less items, jump
    # to the exact index based on the 'digit' pressed. Otherwise, treat the
    # given digit as a percentage, and 
    #
    def digit( self, digit ):
        maxIndex = self.getMaxIndex()
        if maxIndex <= 10:
            if digit == 0: digit = 10
            self.index = min( digit, self.getMaxIndex() ) - 1
        elif digit > 1:
            values = Browser.kDigits[ digit ]
            if digit == self.lastDigit:
                index = self.digitIndex + 1
                if index == len( values ):
                    index = 0
            else:
                index = 0

            value = values[ index ]
            self.lastDigit = digit
            self.digitIndex = index

            #
            # Use binary search to locate the first entry that starts with the
            # value found above.
            #
            lo = 0
            hi = maxIndex
            while lo < hi:
                mid = ( lo + hi ) // 2
                if self.getNameAtIndex( mid )[ 0 ] < value:
                    lo = mid + 1
                else:
                    hi = mid
            self.index = lo

        return self

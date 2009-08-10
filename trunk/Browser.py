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
# collection of objects. Derived classes must define generateWith() to generate
# the line to show for the current object, and getCollection() to obtain the
# collection of objects being browsed.
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

    def __init__( self, iTunes, prevLevel ):
        iTunesSourceGenerator.__init__( self, iTunes )
        self.index = 0          # Index of the current item to show
        self.prevLevel = prevLevel # Link to the previous Browser object
        self.reset()               # Initialize to known state

    def reset( self ):

        #
        # Reset the keyboard jump mechanism
        #
        self.lastDigit = None
        self.digitIndex = 0
        self.nextLevel = None

    #
    # Install handlers for the arrow keys.
    #
    def fillKeyMap( self ):
        iTunesSourceGenerator.fillKeyMap( self )
        self.addKeyMapEntry( kArrowUp, ( kModFirst, kModRepeat ), self.up )
        self.addKeyMapEntry( kArrowDown, ( kModFirst, kModRepeat ), self.down )
        self.addKeyMapEntry( kArrowLeft, ( kModFirst, ), self.left )
        self.addKeyMapEntry( kArrowRight,( kModFirst, ), self.right )

    #
    # Get the largest index for the brosser.
    #
    def getMaxIndex( self ): return len( self.getCollection() )

    #
    # Get the object/value that corresponds to the current index
    #
    def getCurrentObject( self ): return self.getCollection()[ self.index ]

    #
    # Generate an overlay that shows X/Y where X is the current index + 1, and
    # Y is the number of items in the collection
    #
    def getIndexOverlay( self, prefix = '' ):
        if prefix: prefix += ' '
        return '%s%d/%d' % ( prefix, self.index + 1, self.getMaxIndex() )

    #
    # Obtain the list of items being browsed.
    #
    def getCollection( self ):
        raise NotImplementedError, 'getCollection'

    #
    # Obtain a Content object that shows the currently browsed item
    #
    def generateWith( self, obj ):
        raise NotImplementedError, 'generateWith'

    #
    # Implement the Display.generate() interface. Returns a Content object that
    # shows the currently browsed item.
    #
    def generate( self ):
        return self.generateWith( self.getCurrentObject() )

    #
    # Set the current browser index. Key invariant (that we do not check) is
    # that index is always >= 0 and < getMaxIndex()
    #
    def setIndex( self, value ):
        self.index = value
        self.nextLevel = None

    #
    # Move to the previous item in the collection
    #
    def down( self ):
        index = self.index - 1
        if index == -1: index = self.getMaxIndex() - 1
        self.setIndex( index )
        self.reset()
        return self

    #
    # Move to the next item in the collection
    #
    def up( self ):
        index = self.index + 1
        if index == self.getMaxIndex(): index = 0
        self.setIndex( index )
        self.reset()
        return self

    #
    # Use the previous screen generator.
    #
    def left( self ): 
        self.reset()
        return self.prevLevel

    #
    # If there was a previous child browser, show it. Otherwise, invoke
    # makeNextLevel() and return that.
    #
    def right( self ): 
        if not self.nextLevel:
            self.nextLevel = self.makeNextLevel()
        return self.nextLevel

    #
    # Create a new child browser for the currently browsed item. Default
    # implementation does nothing. Derived clases should override to create a
    # more detailed browser.
    #
    def makeNextLevel( self ):
        return None

    #
    # Get the name of the current brows item
    #
    def getNameAtIndex( self, index ):
        return self.getCollection()[ index ].getName()

    #
    # Get the key of the current brows item
    #
    def getKeyAtIndex( self, index ):
        return self.getCollection()[ index ].getKey()

    #
    # Override of DisplayGenerator method. If there are 10 or less items, jump
    # to the exact index based on the 'digit' pressed. Otherwise, treat the
    # given digit as a telephone keypad (similar to Search.py -- see the
    # commentary there)
    #
    def digit( self, digit ):
        maxIndex = self.getMaxIndex()
        if maxIndex <= 10:
            
            #
            # Just select the entry that matches the digit
            #
            if digit == 0: digit = 10
            self.setIndex( min( digit, self.getMaxIndex() ) - 1 )

        elif digit > 1:
            
            #
            # Get the list of characters that correspond to the pressed digit.
            #
            values = Browser.kDigits[ digit ]
            if digit == self.lastDigit:
                
                #
                # Repeated key - cycle to the next character
                #
                index = self.digitIndex + 1
                if index == len( values ):
                    index = 0
            else:
                index = 0

            #
            # Look for the first item that starts with the keypad character
            #
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
                if self.getKeyAtIndex( mid )[ 0 ] < value:
                    lo = mid + 1
                else:
                    hi = mid
            self.setIndex( lo )

        return self

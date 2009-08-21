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

#
# Generic name entry and display. Uses telephone-style keypad letter entry:
#
#      ABC  DEF
#  1    2    3
#
# GHI  JKL  MNO
#  4    5    6
#
# PQRS TUV WXYZ
#  7    8    9
#
#       0
#
# Repeated pressing of the same key cycles through the assigned letters as well
# as the key's numeric digit. Special case is '1', which cycles through the
# digits.
#
# One can also use the up/down arrow keys to change the current character.
# Currently, we only support English alphanumeric characters (A-Z, 0-9).
#
# Press right-arrow to move to a new character position; press twice to submit
# the text to the accept() method. Press the left-arrow to erase the last
# character position; if there are no more, show the previous browser screen.
#
from Content import *
from Display import *
from KeyProcessor import *

class TextEntry( DisplayGenerator ):

    kBlock = '_'                # Character to show at the next position

    #
    # Characters to cycle through for a given digit (eg. pressing '2' three
    # times will leave a 'C' showing)
    #
    kDigits = [ '',
                '1234567890',
                'ABC2',
                'DEF3',
                'GHI4', 
                'JKL5',
                'MNO6',
                'PQRS7',
                'TUV8',
                'WXYZ9' ]

    def __init__( self, client, prevLevel, title, minCount = 3,
                  acceptor = None ):
        DisplayGenerator.__init__( self, client ) 
        self.title = title
        self.prevLevel = prevLevel
        self.minCount = minCount
        self.acceptor = acceptor
        self.reset()

    #
    # Override of Display method. Enable all arrow keys
    #
    def fillKeyMap( self ):
        DisplayGenerator.fillKeyMap( self )
        self.addKeyMapEntry( kArrowUp, ( kModFirst, kModRepeat ), self.up )
        self.addKeyMapEntry( kArrowDown, ( kModFirst, kModRepeat ), self.down )
        self.addKeyMapEntry( kArrowLeft, ( kModFirst, ), self.left )
        self.addKeyMapEntry( kArrowRight, ( kModFirst, ), self.right )
        self.addKeyMapEntry( kOK, (kModFirst, ), self.validateAndAccept )

    #
    # Reset the search parameters to an initial state
    #
    def reset( self ):
        self.text = self.kBlock
        self.lastDigit = None
        self.digitIndex = 0
        self.stack = None

    #
    # Generate the search screen
    #
    def generate( self ):
        return Content( [ self.title, self.text ] )

    def updateLastCharacter( self, value ):
        self.text = self.text[ : -1 ] + value

    #
    # Show the next character in the current position.
    #
    def up( self ):
        value = self.text[ -1 ]
        if value == 'Z':
            value = '0'
        elif value == '9' or value == self.kBlock:
            value = 'A'
        else:
            value = chr( ord( value ) + 1 )
        self.updateLastCharacter( value )
        return self

    #
    # Show the previous character in the current position.
    #
    def down( self ):
        value = self.text[ -1 ]
        if value == 'A':
            value = '9'
        elif value == '0' or value == self.kBlock:
            value = 'Z'
        else:
            value = chr( ord( value ) - 1 )
        self.updateLastCharacter( value )
        return self

    #
    # Process digit keys in a way similar to some text message input systems,
    # where pressing the same digit key cycles through the letters associated
    # with the key.
    #
    def digit( self, digit ):

        #
        # Treat zero as a reset.
        #
        if digit == 0:
            self.reset()
            return self

        values = self.kDigits[ digit ]
        if digit == self.lastDigit:
            index = self.digitIndex + 1
            if index == len( values ):
                index = 0
        else:
            index = 0
        value = values[ index ]
        self.digitIndex = index
        self.lastDigit = digit
        self.updateLastCharacter( value )
        return self

    #
    # Add a character to the text. If done twice in a row, invoke submit()
    #
    def right( self ):

        #
        # If the last character is not a 'new' character, then save the current
        # state digit processing state and add a 'new' character
        #
        if self.terminateText():
            return self
        return self.validateAndAccept()

    def terminateText( self ):

        #
        # If the last character is not a 'new' character, then save the current
        # state digit processing state and add a 'new' character. Unli
        #
        if self.text[ -1 ] != self.kBlock:
            self.stack = ( self.lastDigit, self.digitIndex, self.stack )
            self.text += self.kBlock
            self.lastDigit = None
            self.digitIndex = 0
            return True
        return False

    def validateAndAccept( self ):

        self.terminateText()

        #
        # Strip off the 'new' character and hand the text to the previous
        # level's 'accept' method.
        #
        text = self.text[ : -1 ]
        if not self.validate( text ):
            return self

        return self.accept( text )

    def validate( self, text ):
        return len( text ) >= self.minCount

    def accept( self, text ):
        if self.acceptor:
            return self.acceptor( text )
        raise NotImplementedError, 'accept'

    #
    # Erase characters from the search display. If none left, show the previous
    # level.
    #
    def left( self ):
        if len( self.text ) == 1:
            self.text = self.kBlock
            return self.prevLevel
        self.text = self.text[ : -1 ]
        self.lastDigit, self.digitIndex, self.stack = self.stack
        return self


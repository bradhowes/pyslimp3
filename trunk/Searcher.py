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

from AlbumListBrowser import AlbumListBrowser
from ArtistListBrowser import ArtistListBrowser
from Content import *
from Display import *
from KeyProcessor import *

#
# Generic search term entry and display for album and artist searching. Uses
# telephone-style keypad letter entry:
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
# Press right-arrow to move to a new character position; press twice to execute
# the search. Press the left-arrow to erase the last character position; if
# there are no more, show the previous browser screen.
#
class Searcher( iTunesSourceGenerator ):

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

    def __init__( self, iTunes, prevLevel, tag ):
        iTunesSourceGenerator.__init__( self, iTunes ) 
        self.tag = tag
        self.prevLevel = prevLevel
        self.reset()

    #
    # Override of iTunesSourceGenerator.fillKeyMap. Enable all arrow keys
    #
    def fillKeyMap( self ):
        iTunesSourceGenerator.fillKeyMap( self )
        self.addKeyMapEntry( kArrowUp, ( kModFirst, kModRepeat ), self.up )
        self.addKeyMapEntry( kArrowDown, ( kModFirst, kModRepeat ), self.down )
        self.addKeyMapEntry( kArrowLeft, ( kModFirst, ), self.left )
        self.addKeyMapEntry( kArrowRight, ( kModFirst, ), self.right )

    #
    # Reset the search parameters to an initial state
    #
    def reset( self ):
        self.searchText = self.kBlock
        self.lastDigit = None
        self.digitIndex = 0
        self.stack = None

    #
    # Generate the search screen
    #
    def generate( self ):
        pos = len( self.searchText ) + kDisplayWidth - 1
        return Content( [ self.tag + ' Search Query:',
                          self.searchText ],
                        cursor = pos )

    def updateLastCharacter( self, value ):
        self.searchText = self.searchText[ : -1 ] + value

        
    #
    # Show the next character in the current position.
    #
    def up( self ):
        value = self.searchText[ -1 ]
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
        value = self.searchText[ -1 ]
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
    # Add a character to the search term. If done twice in a row, execute the
    # search and show the results.
    #
    def right( self ):
        
        #
        # If the last character is not a 'new' character, then save the current
        # state digit processing state and add a 'new' character
        #
        if self.searchText[ -1 ] != self.kBlock:
            self.stack = ( self.lastDigit, self.digitIndex, self.stack )
            self.searchText += self.kBlock
            self.lastDigit = None
            self.digitIndex = 0
            return self

        #
        # Execute a search, but only if we have at least 2 characters
        #
        if len( self.searchText ) < 3:
            return self

        #
        # Strip off the 'new' character
        #
        searchText = self.searchText[ : -1 ]
        print 'search text:', searchText
        found = self.searchFor( searchText )
        if found is None:
            found = NoneFound( self, self.tag, searchText )
        return found

    #
    # Erase characters from the search display. If none left, show the previous
    # level.
    #
    def left( self ):
        if len( self.searchText ) == 1:
            self.searchText = self.kBlock
            return self.prevLevel
        self.searchText = self.searchText[ : -1 ]
        self.lastDigit, self.digitIndex, self.stack = self.stack
        return self
    
    def searchFor( self ):
        raise NotImplementedError, 'searchFor'

#
# Specialization of Searcher that peforms searches on album names.
#
class AlbumSearcher( Searcher ):

    def __init__( self, iTunes, prevLevel ):
        Searcher.__init__( self, iTunes, prevLevel, 'Album' ) 

    def searchFor( self, text ):
        found = self.source.searchForAlbum( text )
        if len( found ) == 0: return None
        return AlbumSearchResults( self.source, self, found )

#
# Specialization of AlbumListBrowser that browses the results of the last
# search.
#
class AlbumSearchResults( AlbumListBrowser ):
    def generateWith( self, obj ):
        return Content( [ obj.getName(),
                          obj.getArtistName() ],
                        [ 'Found',
                          self.getIndexOverlay() ] )

#
# Specialization of Searcher that peforms searches on artist names.
#
class ArtistSearcher( Searcher ):

    def __init__( self, iTunes, prevLevel ):
        Searcher.__init__( self, iTunes, prevLevel, 'Artist' ) 

    def searchFor( self, text ):
        found = self.source.searchForArtist( text )
        if len( found ) == 0: return None
        return ArtistSearchResults( self.source, self, found )

#
# Specialization of ArtstListBrowser that browses the results of the last
# search.
#
class ArtistSearchResults( ArtistListBrowser ):
    def generateWith( self, obj ): 
        return Content( [ obj.getName(),
                          formatQuantity( obj.getAlbumCount(), 'album', None,
                                          '(%d %s)' ) ],
                        [ 'Found',
                          self.getIndexOverlay() ] )

#
# Simple display generate that indicates that there are no matches for a given
# search term. The only key supported is 'left'
#
class NoneFound( DisplayGenerator ):

    def __init__( self, prevLevel, context, term ): 
        DisplayGenerator.__init__( self )
        self.context = context
        self.term = term
        self.prevLevel = prevLevel

    def isOverlay( self ): return True

    #
    # Override of DisplayGenerator.fillKeyMap. Enable kArrowLeft.
    #
    def fillKeyMap( self ):
        DisplayGenerator.fillKeyMap( self )
        self.addKeyMapEntry( kArrowLeft, kModFirst, self.left )

    def generate( self ): return Content(
        [ centerAlign( 'No %ss matched' % ( self.context.lower(), ) ),
          centerAlign( self.term ) ] )

    def left( self ): return self.prevLevel

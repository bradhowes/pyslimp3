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
from TextEntry import *

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
class Searcher( TextEntry ):

    def __init__( self, client, prevLevel, tag ):
        TextEntry.__init__( self, client, prevLevel, tag + ' Search Query:' ) 
        self.tag = tag

    #
    # Reset the search parameters to an initial state
    #
    def reset( self ):
        TextEntry.reset( self )
        self.nextLevel = None

    def updateLastCharacter( self, value ):
        TextEntry.updateLastCharacter( self, value )
        self.nextLevel = None

    def accept( self, text ):
        if self.nextLevel:
            return self.nextLevel
        print 'search text:', text
        found = self.searchFor( text )
        if found is None:
            found = NoneFound( self.client, self, self.tag, text )
        self.nextLevel = found
        return found

    #
    # Erase characters from the search display. If none left, show the previous
    # level.
    #
    def left( self ):
        self.nextLevel = None
        return TextEntry.left( self )

    def searchFor( self ):
        raise NotImplementedError, 'searchFor'

#
# Specialization of Searcher that peforms searches on album names.
#
class AlbumSearcher( Searcher ):

    def __init__( self, client, prevLevel ):
        Searcher.__init__( self, client, prevLevel, 'Album' ) 

    def searchFor( self, text ):
        found = self.client.iTunes.searchForAlbum( text )
        if len( found ) == 0: return None
        return AlbumSearchResults( self.client, self, found )

#
# Specialization of AlbumListBrowser that browses the results of the last
# search.
#
class AlbumSearchResults( AlbumListBrowser ):

    def __init__( self, client, prevLevel, found ):
        AlbumListBrowser.__init__( self, client, prevLevel )
        self.found = found

    def getCollection( self ): return self.found

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
        found = self.client.iTunes.searchForArtist( text )
        if len( found ) == 0: return None
        return ArtistSearchResults( self.client, self, found )

#
# Specialization of ArtstListBrowser that browses the results of the last
# search.
#
class ArtistSearchResults( ArtistListBrowser ):
    
    def __init__( self, client, prevLevel, found ):
        ArtistListBrowser.__init__( self, client, prevLevel )
        self.found = found

    def getCollection( self ): return self.found

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
class NoneFound( OverlayDisplay ):

    def __init__( self, client, prevLevel, context, term ): 
        DisplayGenerator.__init__( self, client )
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

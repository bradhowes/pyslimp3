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
from Browser import Browser
from Content import Content
from Display import *
from KeyProcessor import *
from PlaybackDisplay import PlaybackDisplay

#
# Specialization of Browser that shows a list of artists. Handles the kPlay
# keyCode event by asking iTunes to play all of the albums for the active
# artist.
#
class ArtistListBrowser( Browser ):

    #
    # Obtain the collection to browse. Implementation of Browser interface.
    #
    def getCollection( self ): return self.source.getArtistList()

    #
    # Enable 'play'
    #
    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kPlay, None, self.play )

    #
    # Show the current artist name and album count
    #
    def generateWith( self, obj ): 
        return Content( [ obj.getName(),
                          formatQuantity( obj.getAlbumCount(), 'album', None,
                                          '(%d %s)' ) ],
                        [ 'Artist',
                          self.getIndexOverlay() ] )

    #
    # Create and show an AlbumListBrowser for the artist's albums
    #
    def makeNextLevel( self ):
        obj = self.getCurrentObject()
        return AlbumListBrowser( self.client, self, obj.getAlbums() )

    #
    # Begin playback at the start of the first albumn
    #
    def play( self ):
        self.source.playArtist( self.getCurrentObject() )
        return PlaybackDisplay( self.client, self )

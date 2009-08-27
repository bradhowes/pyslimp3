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
from Content import Content
from Display import *
from PlayableBrowser import PlayableBrowser
from PlaybackDisplay import PlaybackDisplay

#
# Specialization of PlayableBrowser that shows a list of genres. Moving right
# shows an AlbumListBrowser for the current genre.
#
class GenreListBrowser( PlayableBrowser ):

    #
    # Implementation of Browser interface. Returns list of Genre objects
    #
    def getCollection( self ): return self.source.getGenreList()

    #
    # Show the current genre name and album count
    #
    def generateWith( self, obj ): 
        return Content( [ obj.getName(),
                          formatQuantity( obj.getAlbumCount(), 'album', None,
                                          '(%d %s)' ) ],
                        [ 'Genre',
                          self.getIndexOverlay() ] )

    #
    # Create an AlbumListBrowser for the genre's albums
    #
    def makeNextLevel( self ): 
        obj = self.getCurrentObject()
        return AlbumListBrowser( self.client, self, obj.getAlbums() )

    #
    # Implementation of the PlayableBrowser interface. Begin playback at the
    # start of the first album
    #
    def play( self ): 
        self.source.playObject( self.getCurrentObject() )
        return PlaybackDisplay( self.client, self )

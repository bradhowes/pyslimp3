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

#
# Specialization of Browser that shows a list of genre names. Moving right
# shows an AlbumListBrowser for the current genre.
#
class GenreListBrowser( Browser ):

    #
    # Implementation of Browser interface. Returns list of genre names
    #
    def getCollection( self ): return self.source.getGenreNames()

    #
    # Obtain the display for the current genre index
    #
    def generateWith( self, obj ): 
        genre = self.source.getGenre( obj )
        return Content( [ obj.getName(),
                          formatQuantity( len( genre ), 'album', None,
                                          '(%d %s)' ) ],
                        [ 'Genre',
                          self.getIndexOverlay() ] )

    #
    # Show an AlbumListBrowser with the list of albums associated with the
    # current genre.
    #
    def makeNextLevel( self ): 
        obj = self.getCurrentObject()
        genre = self.source.getGenre( obj )
        return AlbumListBrowser( self.client, self, genre )

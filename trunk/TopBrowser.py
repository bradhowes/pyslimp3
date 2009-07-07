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
from Browser import Browser
from Content import Content
from GenreListBrowser import GenreListBrowser
from PlaylistBrowser import PlaylistBrowser
from Searcher import AlbumSearcher, ArtistSearcher

#
# Specialization of Browser that shows the top menu options.
#
class TopBrowser( Browser ):

    def __init__( self, iTunes ):
        Browser.__init__( self, iTunes, None )
        self.collection = ( self.browseAlbums,
                            self.browseArtists,
                            self.browseGenres,
                            self.browsePlaylists,
                            self.albumSearcher,
                            self.artistSearcher )
        
    def getCollection( self ): return self.collection

    #
    # Obtain the display content for the current index.
    #
    def generate( self ): 
        return Content( self.getCurrentObject()( True ) )

    #
    # Go down a level and show a different browser.
    #
    def makeNextLevel( self ):
        return self.getCurrentObject()( False )

    def browseAlbums( self, getText ):
        if getText:
            return [ 'Browse Albums', 
                     '(%d total)' % self.source.getAlbumCount() ]
        return AlbumListBrowser( self.source, self )

    def browseArtists( self, getText ):
        if getText:
            return [ 'Browse Artists', 
                     '(%d total)' % self.source.getArtistCount() ]
        return ArtistListBrowser( self.source, self )

    def browseGenres( self, getText ):
        if getText:
            return [ 'Browse Genres', 
                     '(%d total)' % self.source.getGenreCount() ]
        return GenreListBrowser( self.source, self )

    def browsePlaylists( self, getText ):
        if getText:
            return [ 'Browse Playlists', 
                     '(%d total)' % self.source.getPlaylistCount() ]
        return PlaylistBrowser( self.source, self )

    def albumSearcher( self, getText ):
        if getText:
            return [ 'Search',
                     'Albums' ]
        return AlbumSearcher( self.source, self )

    def artistSearcher( self, getText ):
        if getText:
            return [ 'Search',
                     'Artists' ]
        return ArtistSearcher( self.source, self )

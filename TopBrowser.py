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
from DynamicBrowser import *
from Content import Content
from GenreListBrowser import GenreListBrowser
from PlaylistBrowser import PlaylistBrowser
from Searcher import AlbumSearcher, ArtistSearcher

#
# DynamicEntry derivative that for albums
#
class BrowseAlbums( DynamicEntry ):
    def makeContent( self, browser ): 
        return [ 'Browse Albums',
                 '(%d total)' % browser.getSource().getAlbumCount() ]
    def makeNextLevel( self, browser ):
        if browser.getSource().getAlbumCount() == 0:
            return browser
        return AlbumListBrowser( browser.client, browser )

#
# DynamicEntry derivative that for artists
#
class BrowseArtists( DynamicEntry ):
    def makeContent( self, browser ): 
        return [ 'Browse Artists',
                 '(%d total)' % browser.getSource().getArtistCount() ]
    def makeNextLevel( self, browser ):
        if browser.getSource().getArtistCount() == 0:
            return browser
        return ArtistListBrowser( browser.client, browser )

#
# DynamicEntry derivative that for genres
#
class BrowseGenres( DynamicEntry ):
    def makeContent( self, browser ): 
        return [ 'Browse Genres',
                 '(%d total)' % browser.getSource().getGenreCount() ]
    def makeNextLevel( self, browser ):
        if browser.getSource().getGenreCount() == 0:
            return browser
        return GenreListBrowser( browser.client, browser )

#
# DynamicEntry derivative that for playlists
#
class BrowsePlaylists( DynamicEntry ):
    def makeContent( self, browser ): 
        return [ 'Browse Playlists',
                 '(%d total)' % browser.getSource().getPlaylistCount() ]
    def makeNextLevel( self, browser ):
        if browser.getSource().getPlaylistCount() == 0:
            return browser
        return PlaylistBrowser( browser.client, browser )

#
# DynamicEntry derivative that for playlists
#
class SearchAlbums( DynamicEntry ):
    def makeContent( self, browser ): 
        return [ 'Search', 'Albums' ]
    def makeNextLevel( self, browser ):
        return AlbumSearcher( browser.client, browser )

#
# DynamicEntry derivative that for playlists
#
class SearchArtists( DynamicEntry ):
    def makeContent( self, browser ): 
        return [ 'Search', 'Artists' ]
    def makeNextLevel( self, browser ):
        return ArtistSearcher( browser.client, browser )

#
# Specialization of Browser that shows the top menu options.
#
class TopBrowser( DynamicBrowser ):

    def __init__( self, client ):
        DynamicBrowser.__init__( self, client, None,
                                 ( BrowseAlbums(),
                                   BrowseArtists(),
                                   BrowseGenres(),
                                   BrowsePlaylists(),
                                   SearchAlbums(),
                                   SearchArtists() ) )

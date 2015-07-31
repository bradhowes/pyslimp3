#
# Copyright (C) 2009, 2010 Brad Howes.
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

from PlayableBrowser import *
from Content import Content
from Display import *
from KeyProcessor import *
from PlaybackDisplay import PlaybackDisplay
from RatingDisplay import *
from TrackListBrowser import *

#
# Specialization of Browser that shows a list of albums. Handles the kPlay
# keyCode event by asking iTunes to play the active album. Displays either all
# albums found in iTunes (default) or a subset of those albums associated with
# a particular artist.
#
class AlbumListBrowser( PlayableBrowser ):

    def __init__( self, client, prevLevel, albumList = None ):
        PlayableBrowser.__init__( self, client, prevLevel )
        self.albumList = albumList

    #
    # Obtain the collection to browse. Implementation of Browser interface.
    #
    def getCollection( self ): 
        if self.albumList is None:
            return self.source.getAlbumList()
        return self.albumList

    #
    # Enable 'PIP' for ratings
    #
    def fillKeyMap( self ):
        PlayableBrowser.fillKeyMap( self )
        self.addKeyMapEntry( kPIP, None, self.ratings )

    #
    # Show the current album name and track count
    #
    def generateWith( self, obj ):
        return Content( [ obj.getName(),
                          obj.getArtistName() ],
                        [ 'Album',
                          self.getIndexOverlay() ] )

    #
    # Create and show a TrackListBrowser for the album tracks
    #
    def makeNextLevel( self ):
        obj = self.getCurrentObject()
        return TrackListBrowser( self.client, self, obj.getTracks() )

    #
    # Implementation of the PlayableBrowser interface. Begin playback at the
    # start of the album (or at the track at the given index)
    #
    def play( self, trackIndex = 0 ): 
        self.source.playObject( self.getCurrentObject(), trackIndex )
        return PlaybackDisplay( self.client, self )

    #
    # Show ratings editor for the album
    #
    def ratings( self ):
        return AlbumRatingDisplay( self.client, self, self.getCurrentObject() )

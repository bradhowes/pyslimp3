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

from Browser import Browser
from Content import Content
from Display import *
from KeyProcessor import *
from PlaybackDisplay import PlaybackDisplay
from RatingDisplay import *
from TrackListBrowser import *

#
# Specialization of Browser that shows a list of albums. Handles the kPlay
# keyCode event by asking iTunes to play the active album.
#
class AlbumListBrowser( Browser ):

    def __init__( self, iTunes, prevLevel, albumList ):
        Browser.__init__( self, iTunes, prevLevel, albumList )

    #
    # Enable 'play'
    #
    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kPlay, None, self.play )
        self.addKeyMapEntry( kPIP, None, self.ratings )

    def getNameAtIndex( self, index ):
        return self.collection[ index ].getName()

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
    def right( self ):
        obj = self.getCurrentObject()
        title = obj.getName() + ' - ' + obj.getArtistName()
        return TrackListBrowser( self.source, self, obj.getTracks(), title,
                                 trackNameFormatter )

    #
    # Begin playback at the start of the album (or at the track at the given
    # index)
    #
    def play( self, trackIndex = 0 ): 
        self.source.playAlbum( self.getCurrentObject(), trackIndex )
        return PlaybackDisplay( self.source, self )

    def ratings( self ):
        return AlbumRatingDisplay( self.source, self, self.getCurrentObject() )

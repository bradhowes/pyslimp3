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

from Content import Content
from Display import getHHMMSS
from KeyProcessor import *
from PlayableBrowser import *
from RatingDisplay import *

#
# Specialization of Browser that shows a list of tracks associated with an
# album or playlist. Pressing the 'play' key will start playing at the
# indicated track
#
class TrackListBrowser( PlayableBrowser ):

    def __init__( self, client, prevLevel, trackList ):
        PlayableBrowser.__init__( self, client, prevLevel )
        self.trackList = trackList

    def getCollection( self ): return self.trackList

    #
    # Enable 'play'
    #
    def fillKeyMap( self ):
        PlayableBrowser.fillKeyMap( self )
        self.addKeyMapEntry( kPIP, None, self.ratings )
        self.addKeyMapEntry( kArrowRight, None, self.ratings )

    #
    # Show the current track name and duration values
    #
    def generateWith( self, obj ): 
        return Content( [ obj.getAlbumName() + 
                          unichr( CustomCharacters.kDottedVerticalBar ) + 
                          obj.getArtistName(),
                          obj.getName() ],
                        [ 'Track',
                          self.getIndexOverlay() ] )

    #
    # Implementation of the PlayableBrowser interace. Begin playback at the
    # current track.
    #
    def play( self ): 
        if self.prevLevel:
            return self.prevLevel.play( self.index )
        return None

    #
    # Show the user ratings for the current track
    #
    def ratings( self ):
        return TrackRatingDisplay( self.client, self, self.getCurrentObject() )

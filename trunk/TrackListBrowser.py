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
from Display import getHHMMSS
from KeyProcessor import *

#
# Specialization of Browser that shows a list of tracks associated with an
# album or playlist. Pressing the 'play' key will start playing at the
# indicated track
#
def trackNameFormatter( track ): 
    return track.getName()

def trackAlbumNameFormatter( track ): 
    return trackNameFormatter( track ) + ' - ' + track.getAlbumName()

def trackAlbumArtistNameFormatter( track ): 
    return trackAlbumNameFormatter( track ) + ' - ' + track.getArtistName()

class TrackListBrowser( Browser ):

    def __init__( self, iTunes, prevLevel, trackList, title,
                  formatter ):
        Browser.__init__( self, iTunes, prevLevel, trackList )
        self.title = title
        self.formatter = formatter

    #
    # Enable 'play'
    #
    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kPlay, None, self.play )

    #
    # Show the current track name and duration values
    #
    def generateWith( self, obj ): 
        return Content( [ self.formatter( obj ),
                          self.title ],
                        [ self.getIndexOverlay(),
                          getHHMMSS( obj.getDuration() ) ] )

    #
    # Begin playback at the current track.
    #
    def play( self ): 
        if self.prevLevel:
            return self.prevLevel.play( self.index )
        return None

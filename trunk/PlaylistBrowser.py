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
from TrackListBrowser import *

#
# Specialization of Browser that shows a list of playlists found in the iTunes
# application. Pressing the 'play' key will start playing the indicated
# playlist.
#
class PlaylistBrowser( Browser ):

    def __init__( self, iTunes, prevLevel ):
        Browser.__init__( self, iTunes, prevLevel )
        
    def getCollection( self ): return self.source.getPlaylistList()

    #
    # Enable 'play'
    #
    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kPlay, None, self.play )

    #
    # Show the current playlist name and track count
    #
    def generateWith( self, obj ): 
        return Content( [ obj.getName(),
                          formatQuantity( obj.getTrackCount(), 'trk', None,
                                          '(%d %s)' ) ],
                        [ 'Playlist',
                          self.getIndexOverlay() ] )

    #
    # Create and show a TrackListBrowser for the playlist tracks
    #
    def makeNextLevel( self ):
        obj = self.getCurrentObject()
        if obj.getTrackCount() == 0:
            return None
        return TrackListBrowser( self.source, self, obj.getTracks() )

    #
    # Begin playback at the start of the playlist (or at the track at the given
    # index)
    #
    def play( self, trackIndex = 0 ): 
        self.source.playPlaylist( self.getCurrentObject(), trackIndex )
        return PlaybackDisplay( self.source, self )

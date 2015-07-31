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
from Display import NotificationDisplay
from KeyProcessor import *

#
# Derivation of Browser that supports REC and PLAY keys.
#
class PlayableBrowser( Browser ):

    #
    # Install handler for the REC button to add the track(s) of the current
    # object to the target playlist.
    #
    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kRecord, kModFirst, self.record )
        self.addKeyMapEntry( kPlay, kModFirst, self.play )

    #
    # Add the current object to the target playlist.
    #
    def record( self ):

        #
        # Ask the object to add itself to the target playlist.
        #
        obj = self.getCurrentObject()
        playlist = self.source.getPlaylist(
            self.client.getSettings().getTargetPlaylistName() )
        obj.addToPlaylist( playlist )

        #
        # Notify the user that we did it
        #
        return NotificationDisplay( self.client, self, 
                                    u'Added ' + obj.getName(),
                                    u'to playlist ' + playlist.getName() )

    #
    # Action performed when the user presses the 'play' key. Derived classes
    # must define.
    #
    def play( self ):
        raise NotImplementedError, 'play'

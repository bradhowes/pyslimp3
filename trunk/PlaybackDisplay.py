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
from Display import *
from KeyProcessor import *
from RatingDisplay import *

#
# Display generator showing current playing status of iTunes. Responds to
# various keyCode events to control iTunes playback.
#
class PlaybackDisplay( iTunesSourceGenerator ):

    kPlayerState = { 'k.playing': '',
                     'k.paused': 'Paused',
                     'k.stopped': 'Stopped',
                     'k.fast_forwarding': 'FFWD',
                     'k.rewinding': 'RWD'
                     }

    def __init__( self, source, prevLevel ):
        iTunesSourceGenerator.__init__( self, source )
        self.prevLevel = prevLevel

    def fillKeyMap( self ):
        iTunesSourceGenerator.fillKeyMap( self )
        self.addKeyMapEntry( kArrowLeft, None, self.left )
        self.addKeyMapEntry( kArrowRight, None, self.ratings )
        self.addKeyMapEntry( kPIP, None, self.ratings )
        self.addKeyMapEntry( kStop, None, self.stop )
        self.addKeyMapEntry( kPlay, None, self.play )
        self.addKeyMapEntry( kPause, None, self.pause )

        self.addKeyMapEntry( kRewind, kModRelease, self.previousTrack )
        self.addKeyMapEntry( kRewind, kModHeld, self.rewind )
        self.addKeyMapEntry( kRewind, kModReleaseHeld, self.resume )

        self.addKeyMapEntry( kFastForward, kModRelease, self.nextTrack )
        self.addKeyMapEntry( kFastForward, kModHeld, self.fastForward )
        self.addKeyMapEntry( kFastForward, kModReleaseHeld, self.resume )

    #
    # Generate a screen showing what is playing, the current iTunes playback
    # state, and the playback position in MM:SS.
    #
    def generate( self ):
        track = self.source.getCurrentTrack()
        line1 = '%s - %s' % ( track.getAlbumName(), track.getArtistName() )
        line2 = '%d.%s' % ( track.getIndex(), track.getName() )
        state = self.kPlayerState.get( self.source.getPlayerState(), '???' )
        position = getHHMMSS( self.source.getPlayerPosition() )
        return Content( [ line1, 
                          line2 ],
                        [ state, 
                          position ] )

    #
    # Show any previous display.
    #
    def left( self ):
        if self.prevLevel:
            return self.prevLevel
        return self

    def ratings( self ):
        return TrackRatingDisplay( self.source, self,
                                   self.source.getCurrentTrack() )

    #
    # iTunes controls
    #
    def previousTrack( self ):
        self.source.previousTrack()
        return self

    def nextTrack( self ):
        self.source.nextTrack()
        return self

    def stop( self ): 
        self.source.stop()
        return self

    def play( self ):
        self.source.play()
        return self

    def pause( self ):
        self.source.pause()
        return self

    def rewind( self ): 
        self.source.rewind()
        return self

    def fastForward( self ): 
        self.source.fastForward()
        return self

    def resume( self ):
        self.source.resume()
        return self

    #
    # Use the '0' key to restart the current track.
    #
    def digit0( self ):
        self.source.beginTrack()
        return self

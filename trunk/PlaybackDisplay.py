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
                     'k.paused': 'PAUSE',
                     'k.stopped': 'STOP',
                     'k.fast_forwarding': 'FFWD',
                     'k.rewinding': 'RWD'
                     }

    #
    # Constructor. 
    #
    def __init__( self, source, prevLevel, formatterIndex = 0 ):
        iTunesSourceGenerator.__init__( self, source )
        self.prevLevel = prevLevel
        self.formatterIndex = formatterIndex
        self.formatters = ( self.getPlayerPositionIndicator,
                            self.getPlayerPositionElapsed,
                            self.getPlayerPositionRemaining )
        self.getPlayerPosition = self.formatters[ self.formatterIndex ]

    def getFormatterIndex( self ):
        return self.formatterIndex

    #
    # Override of iTunesSourceGenerator method. Install our own keymap entries.
    #
    def fillKeyMap( self ):
        iTunesSourceGenerator.fillKeyMap( self )
        
        #
        # If we arrived here from the user pressing the 'Disp' button, allow
        # them to return to the previous location.
        #
        self.addKeyMapEntry( kArrowLeft, None, self.left )
        
        #
        # Show and edit the rating for the current track
        #
        self.addKeyMapEntry( kArrowRight, None, self.ratings )
        self.addKeyMapEntry( kPIP, None, self.ratings )

        #
        # Stop playing, rewinding to the beginning of track
        #
        self.addKeyMapEntry( kStop, None, self.stop )
        
        #
        # Start playing if not already
        #
        self.addKeyMapEntry( kPlay, None, self.play )
        
        #
        # Stop playing, but do not rewind to beginning of track
        #
        self.addKeyMapEntry( kPause, None, self.pause )

        #
        # Move to previous track if not held down.
        #
        self.addKeyMapEntry( kRewind, kModRelease, self.previousTrack )
        
        #
        # Rewind playback position while held down
        #
        self.addKeyMapEntry( kRewind, kModHeld, self.rewind )
        
        #
        # Resume normal playback once released
        #
        self.addKeyMapEntry( kRewind, kModReleaseHeld, self.resume )

        #
        # Move to next track if not held down
        #
        self.addKeyMapEntry( kFastForward, kModRelease, self.nextTrack )
        
        #
        # Fast-forward playback positiono while held down
        #
        self.addKeyMapEntry( kFastForward, kModHeld, self.fastForward )
        
        #
        # Resume normal playback once released
        #
        self.addKeyMapEntry( kFastForward, kModReleaseHeld, self.resume )

    #
    # Install the next available display formatter
    #
    def nextPlayerPositionFormatter( self ):
        self.formatterIndex = ( self.formatterIndex + 1) % \
            len( self.formatters )
        self.getPlayerPosition = self.formatters[ self.formatterIndex ]

    #
    # Generate a screen showing what is playing, the current iTunes playback
    # state, and the playback position.
    #
    def generate( self ):
        track = self.source.getCurrentTrack()
        line1 = '%s - %s' % ( track.getAlbumName(), track.getArtistName() )
        line2 = '%d.%s' % ( track.getIndex(), track.getName() )
        state = self.getPlayerState( track )
        return Content( [ line1, 
                          line2 ],
                        [ '', 
                          state ] )

    def getPlayerState( self, track ):
        state = self.kPlayerState.get( self.source.getPlayerState(), '???' )
        if state == '':
            if self.source.getMute():
                state = 'MUTED'
        if state == '':
            state = self.getPlayerPosition( track )
        return state

    def getPlayerPositionIndicator( self, track ):
        position = float( self.source.getPlayerPosition() ) / \
            track.getDuration()
        return generateProgressIndicator( 10, position )

    def getPlayerPositionElapsed( self, track ):
        return getHHMMSS( self.source.getPlayerPosition() )

    def getPlayerPositionRemaining( self, track ):
        return '-' + getHHMMSS( track.getDuration() - 
                                self.source.getPlayerPosition() )

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

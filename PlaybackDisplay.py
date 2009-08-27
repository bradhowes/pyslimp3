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
from TrackListBrowser import TrackListBrowser

#
# Display generator showing current playing status of iTunes. Responds to
# various keyCode events to control iTunes playback.
#
class PlaybackDisplay( DisplayGenerator ):

    #
    # Mapping of iTunes player state to a status string
    #
    kPlayerState = { 'k.playing': '',
                     'k.paused': 'PAUSED',
                     'k.stopped': 'STOPPED',
                     'k.fast_forwarding': 'FFWD',
                     'k.rewinding': 'RWD'
                     }

    #
    # Constructor. 
    #
    def __init__( self, client, prevLevel ):
        if prevLevel is None:
            raise RuntimeError, 'prevLevel is None'

        DisplayGenerator.__init__( self, client, prevLevel )
        self.formatters = ( self.getPlayerTrackIndex,
                            self.getPlayerPositionElapsed,
                            self.getPlayerPositionRemaining,
                            self.getPlayerTrackDuration,
                            self.getEmptyString )

        #
        # Obtain the last formatter setting in use.
        #
        self.setFormatterIndex(
            client.getSettings().getPlaybackFormatterIndex() )

    #
    # Set the position formatter index to a new value.
    #
    def setFormatterIndex( self, value ):

        #
        # Make sure that the value is valid
        #
        if value < 0: 
            value = 0
        elif value >= len( self.formatters ):
            value = len( self.formatters ) - 1

        #
        # Install the new value and remember it in the client's settings
        #
        self.getPlayerPosition = self.formatters[ value ]
        self.formatterIndex = value
        self.client.getSettings().setPlaybackFormatterIndex( value )

    #
    # Override of Display method. Install our own keymap entries.
    #
    def fillKeyMap( self ):
        DisplayGenerator.fillKeyMap( self )

        self.addKeyMapEntry( kArrowUp, None, 
                             self.nextTrackBrowser )

        self.addKeyMapEntry( kArrowDown, None, 
                             self.previousTrackBrowser )

        #
        # Show and edit the rating for the current track
        #
        self.addKeyMapEntry( kArrowRight, None, self.ratings )
        self.addKeyMapEntry( kPIP, None, self.ratings )

        #
        # Start playing if not already
        #
        self.addKeyMapEntry( kPlay, None, self.play )

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
        # Use the next available dislay formatter
        #
        self.addKeyMapEntry( kDisplay, kModFirst, 
                             self.nextPlayerPositionFormatter )

    #
    # Install the next available display formatter
    #
    def nextPlayerPositionFormatter( self ):
        index = ( self.formatterIndex + 1 ) % len( self.formatters )
        self.setFormatterIndex( index )

    def nextTrackBrowser( self ):
        playlist = self.source.getActivePlaylist()
        index = playlist.getTrackIndex( self.source.getCurrentTrack() ) + 1
        if index >= playlist.getTrackCount():
            index = 0
        return TrackListBrowser( self.client, self, playlist.getTracks(), 
                                 index, True )

    def previousTrackBrowser( self ):
        playlist = self.source.getActivePlaylist()
        index = playlist.getTrackIndex( self.source.getCurrentTrack() ) - 1
        if index < 0:
            index = playlist.getTrackCount() - 1
        return TrackListBrowser( self.client, self, playlist.getTracks(), 
                                 index, True )

    def unrecord( self, trackIndex ):
        print( 'unrecord', trackIndex )
        playlist = self.source.getActivePlaylist()
        if not playlist.getCanManipulate():
            return self
        playlist.removeTrack( trackIndex )
        if playlist.getTrackCount() == 0:
            return self.prevLevel
        return self

    #
    # Generate a screen showing what is playing, the current iTunes playback
    # state, and the playback position.
    #
    def generate( self ):
        track = self.source.getCurrentTrack()
        line1 = track.getAlbumName() + \
            unichr( CustomCharacters.kDottedVerticalBar ) + \
            track.getArtistName()
        line2 = track.getName()
        state = self.getPlayerState( track )
        return Content( [ line1, 
                          line2 ],
                        [ state, 
                          self.getPlayerPosition( track ) ] )

    #
    # Obtain a string representing the current iTunes player state.
    #
    def getPlayerState( self, track ):
        state = self.kPlayerState.get( self.source.getPlayerState(), '???' )
        if state == '':
            if self.source.getMute():
                state = 'MUTED'
        if state == '':
            state = self.getPlayerPositionIndicator( track )
        else:
            state = unichr( CustomCharacters.kEllipsis ) + state
        return state

    #
    # Obtain an empty string. This is one of the custom position indicators.
    #
    def getEmptyString( self, track ):
        return ''

    #
    # Obtain the current track index and the total track count. This is one of
    # the custom position indicators.
    #
    def getPlayerTrackIndex( self, track ):
        playlist = self.source.getActivePlaylist()
        return '%d/%d' % ( playlist.getTrackIndex( track ) + 1,
                           playlist.getTrackCount() )

    #
    # Obtain a graphical progress indicator showing how much of the song has
    # elapsed.
    #
    def getPlayerPositionIndicator( self, track ):
        position = float( self.source.getPlayerPosition() ) / \
            track.getDuration()
        return generateProgressIndicator( 5, position )

    #
    # Obtain a numerical elapsed indicator in MM:SS format.
    #
    def getPlayerPositionElapsed( self, track ):
        return '+' + getHHMMSS( self.source.getPlayerPosition() )

    #
    # Obtain a numerical remaining indicator in MM:SS format.
    #
    def getPlayerPositionRemaining( self, track ):
        return '-' + getHHMMSS( track.getDuration() - 
                                self.source.getPlayerPosition() )

    #
    # Obtain the duration for the current track.
    #
    def getPlayerTrackDuration( self, track ):
        return getHHMMSS( track.getDuration() )

    #
    # Show a track rating editor for the current track.
    #
    def ratings( self ):
        return TrackRatingDisplay( self.client, self,
                                   self.source.getCurrentTrack() )

    #
    # Move to the previous track in the current playlist
    #
    def previousTrack( self ):
        self.source.previousTrack()
        return self
    #
    # Move to the next track in the current playlist
    #
    def nextTrack( self ):
        self.source.nextTrack()
        return self

    #
    # Stop iTunes playback, and reset the playback position to the start of the
    # current track.
    #
    def stop( self ): 
        self.source.stop()
        return self

    #
    # Begin iTunes playback.
    #
    def play( self, trackIndex = -1 ):
        if trackIndex == -1:
            self.source.play()
        else:
            self.source.getActivePlaylist().play( trackIndex )
        return self

    #
    # Stop iTunes playback, but leave the playback position where it is.
    #
    def pause( self ):
        self.source.pause()
        return self

    #
    # Move the current playback postion back in time.
    #
    def rewind( self ): 
        self.source.rewind()
        return self

    #
    # Move the current playback postion forward in time.
    #
    def fastForward( self ): 
        self.source.fastForward()
        return self

    #
    # Stop the rewind() or fastForward() behavior, resuming normal iTunes
    # playback
    #
    def resume( self ):
        self.source.resume()
        return self

    #
    # Use the '0' key to restart the current track. Otherwise, treat as an
    # index of the track to play (1-9). Override of DisplayGenerator method.
    #
    def digit( self, digit ):
        source = self.source
        if digit == 0:
            source.beginTrack()
        else:
            playlist = source.getActivePlaylist()
            count = playlist.getTrackCount()
            if digit <= count:
                playlist.play( digit - 1 )
        return self

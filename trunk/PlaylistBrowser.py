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
from TextEntry import *
from TrackListBrowser import *
from YesNoEntry import *

#
# Specialization of Browser that shows a list of playlists found in the iTunes
# application. Pressing the 'play' key will start playing the indicated
# playlist.
#
class PlaylistBrowser( Browser ):

    #
    # Constructor. Show as the first element the playlist that is the current
    # target.
    #
    def __init__( self, client, prevLevel = None ):
        Browser.__init__( self, client, prevLevel )
        self.showTargetPlaylist()

    #
    # Implementation of Browser interface
    #
    def getCollection( self ): return self.source.getPlaylistList()

    #
    # Enable the following key mappings:
    # - play: start playing the current playlist
    # - record: obtain the name for a new playlist
    # - 0 (zero): clear or delete the current playlist
    # - OK: make the current playlist the target playlist
    #
    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kPlay, None, self.play )
        self.addKeyMapEntry( kRecord, None, self.createPlaylist )
        self.addKeyMapEntry( kDigit0, None, self.clearOrDeletePlaylist )
        self.addKeyMapEntry( kOK, None, self.clearOrSetTargetPlaylist )

    #
    # Get the target playlist name.
    #
    def getTargetPlaylistName( self ):
        name = self.client.getSettings().getTargetPlaylistName()
        if name == '':
            name = self.source.kOurPlaylistName
        return name

    #
    # Set the target playlist setting, where NAME if given is the name of the
    # playlist to use.
    #
    def setTargetPlaylistName( self, name = None ):
        if name is None:
            name = self.getCurrentObject().getName()
        self.client.getSettings().setTargetPlaylistName( name )

    #
    # Clear the target playlist setting, making the MBJB playlist the target
    #
    def clearTargetPlaylistName( self ):
        self.client.getSettings().setTargetPlaylistName( 
            self.source.kOurPlaylistName )

    #
    # Determine if the currently shown playlist is the target playlist
    #
    def isShowingTargetPlaylistName( self ):
        return self.getCurrentObject().getName() == self.getTargetPlaylistName()

    #
    # Locate the playlist in the list of playlists that is the target playlist.
    # and make our internal index match it.
    #
    def showTargetPlaylist( self ):
        target = self.getTargetPlaylistName()
        playlists = self.getCollection()
        for index in range( len( playlists ) ):
            if playlists[ index ].getName() == target:
                self.index = index
                break

    #
    # Show the current playlist name and track count
    #
    def generateWith( self, obj ):
        if self.isShowingTargetPlaylistName():
            tag = u', *REC*)'
        elif not obj.getCanManipulate():
            tag = u', read-only)'
        else:
            tag = u')'
        line1 = obj.getName()
        line2 = formatQuantity( obj.getTrackCount(), u'track', None,
                                '(%d %s' + tag )
        return Content( [ line1, line2 ],
                        [ 'Playlist', self.getIndexOverlay() ] )

    #
    # Create and show a TrackListBrowser for the playlist tracks
    #
    def makeNextLevel( self ):
        obj = self.getCurrentObject()
        if obj.getTrackCount() == 0:
            return None
        return TrackListBrowser( self.client, self, obj.getTracks() )

    #
    # Begin playback at the start of the playlist (or at the track at the given
    # index)
    #
    def play( self, trackIndex = 0 ): 
        obj = self.getCurrentObject()
        if obj.getTrackCount() > 0:
            self.getCurrentObject().play( trackIndex )
            return PlaybackDisplay( self.client, self )
        return self

    #
    # Show a text entry display to obtain a new playlist name.
    #
    def createPlaylist( self ):
        return TextEntry( self.client, self, u'New playlist name:', 2,
                          self.doCreatePlaylist )

    #
    # Build a NotificationDisplay to confirm the clear or delete action. Which
    # action depends on whether the playlist contains tracks.
    #
    def clearOrDeletePlaylist( self ):
        playlist = self.getCurrentObject()
        if not playlist.getCanManipulate():
            return self
        if playlist.getTrackCount() > 0:
            title = u'Clear playlist "%s"?' % ( playlist.getName(), )
            proc = self.doClearPlaylist
        else:
            title = u'Delete playlist "%s"?' % ( playlist.getName(), )
            proc = self.doDeletePlaylist
        return YesNoEntry( self.client, self, title, proc )

    #
    # Toggle the target attribute for the current playlist. Target playlists
    # acquire tracks from REC operations by the user while browsing the iTunes
    # library.
    #
    def clearOrSetTargetPlaylist( self ):
        playlist = self.getCurrentObject()
        if not playlist.getCanManipulate():
            return self
        if self.isShowingTargetPlaylistName():
            self.clearTargetPlaylistName()
        else:
            self.setTargetPlaylistName()
        return self

    #
    # Create a new playlist under the NAME name
    #
    def doCreatePlaylist( self, name ):
        print( 'new playlist name:', name )
        playlist = self.source.createPlaylist( name )
        if playlist:

            #
            # It worked! Make it the target playlist.
            #
            self.setTargetPlaylistName( playlist.getName() )
            self.showTargetPlaylist()
            return NotificationDisplay( self.client, self,
                                        u'Created new playlist', name )
        else:

            #
            # It failed! Perhaps the name is duplicate.
            #
            return NotificationDisplay( self.client, self,
                                        u'Failed to create playlist', name )
        return self

    #
    # Delete the playlist from iTunes.
    #
    def doDeletePlaylist( self ):
        self.source.deletePlaylist( self.getCurrentObject() )

        #
        # Make sure our internal index value is still sane.
        #
        if self.index == len( self.getCollection() ):
            self.index -= 1
            if self.index == 0:
                return self.left()
        return self

    #
    # Clear the current playlist, removing all its tracks
    #
    def doClearPlaylist( self ):
        self.getCurrentObject().clear()
        return self

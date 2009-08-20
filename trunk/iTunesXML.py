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

import appscript, subprocess, threading, urllib
from bisect import bisect_left
from datetime import datetime
from os import stat
from stat import *
import xml.parsers.expat
from OrderedItem import OrderedItem

#
# Class for an artist. Maintains a list of albums associated with the artist.
#
class Artist( OrderedItem ):
    def __init__( self, name ):
        OrderedItem.__init__( self, name )
        self.albums = []
        self.needSort = True
    def addAlbum( self, album ): self.albums.append( album )
    def getAlbums( self ):
        if self.needSort:
            self.albums.sort()
            self.needSort = False
        return self.albums
    def getAlbumCount( self ): return len( self.albums )
    def getAlbum( self, index ): return self.getAlbums()[ index ]
    def __repr__( self ): return 'Artist "%s"' % ( self.getName(), )

#
# Class for an 'album' created by an artist. Maintains a list of tracks that
# make up the album.
#
class Album( OrderedItem ):
    def __init__( self, artist, name ):
        OrderedItem.__init__( self, name )
        self.artist = artist
        self.tracks = []
        self.needSort = True
    def addTrack( self, track ): self.tracks.append( track )
    def getArtistName( self ): return self.artist.getName()
    def getTracks( self ): 
        if self.needSort:
            self.tracks.sort()
            self.needSort = False
        return self.tracks
    def getTrackCount( self ): return len( self.tracks )
    def getTrack( self, index ): return self.getTracks()[ index ]
    def __repr__( self ): return 'Album "%s"' % ( self.getName(), )

#
# Class for a playlist in iTunes.
#
class Playlist( OrderedItem ):
    def __init__( self, name ):
        OrderedItem.__init__( self, name )
        self.tracks = []
    def getTracks( self ): return self.tracks
    def getTrackCount( self ): return len( self.tracks )
    def getTrack( self, index ): return self.tracks[ index ]
    def getTracks( self ): return self.tracks
    def __repr__( self ): return 'Playlist "%s"' % ( self.getName(), )

#
# Class for a track of an album of an artist. Contains the original iTunes
# XML element object that describes the track.
#
class Track( object ):
    def __init__( self, track ):
        self.track = track
        self.id = str( track.get( 'Persistent ID' ) )
        self.index = int( track.get( 'Track Number', '-1' ) )
        self.name = track.get( 'Name', '' )
        self.artistName = track.get( 'Artist', '' )
        self.albumName = track.get( 'Album', '' )
        self.duration = int( track.get( 'Total Time', 0 ) ) / 1000
    def getID( self ): return self.id
    def getIndex( self ): return self.index
    def getName( self ): return self.name
    def getArtistName( self ): return self.artistName
    def getAlbumName( self ): return self.albumName
    def getDuration( self ): return self.duration
    def __repr__( self ): return 'Track "%d - %s"' % ( self.index, self.name, )
    def hash( self ): return self.index
    def __cmp__( self, other ): return cmp( self.index, other.index )

#
# Wrapper class for a track object obtained from the appscript AppleScript
# bridge. The naming of attributes is different from Track.
#
class ActiveTrack( object ):
    def __init__( self, track ):
        self.track = track
        self.id = track.persistent_ID()
        self.index = track.track_number()
        self.name = track.name()
        self.artistName = track.artist()
        self.albumName = track.album()
        self.duration = track.duration()
    def getID( self ): return self.id
    def getIndex( self ): return self.index
    def getName( self ): return self.name
    def getArtistName( self ): return self.artistName
    def getAlbumName( self ): return self.albumName
    def getDuration( self ): return self.duration
    def __repr__( self ): return 'Track "%d - %s"' % ( self.index, self.name, )
    def hash( self ): return self.index
    def __cmp__( self, other ): return cmp( self.index, other.index )

#
# Parser for the iTunes Music Library.xml file.
#
class XMLParser( object ):

    def __init__( self, path ):

        #
        # Install XML parser hooks
        #
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.startElement
        self.parser.EndElementHandler = self.endElement
        self.parser.CharacterDataHandler = self.characterData

        #
        # Initialize XML parser containers
        #
        self.stack = None
        self.container = None
        self.key = None
        self.value = ''

        #
        # Parse the given file.
        #
        self.parser.ParseFile( open( path ) )

    #
    # XML parsing hook invoked at the start of an element.
    #
    def startElement( self, name, atts ):
        self.value = ''
        
        #
        # Create a new container if appropriate
        #
        if name == 'dict':
            container = {}
        elif name == 'array':
            container = []
        else:
            return

        #
        # Link the new container into an existing one: append to the end of a
        # list or add to a dictionary with the last key value.
        #
        if self.stack is None:
            self.container = container
        elif self.key is not None:
            self.container[ self.key ] = container
            self.key = None
        else:
            self.container.append( container )

        #
        # Update stack of open containers
        #
        self.stack = ( self.container, self.stack )
        self.container = container

    #
    # XML parsing hook invoked at the end of an element. Updates state
    # variables.
    #
    def endElement( self, name ):
        if name == 'key':       # Remember the last <key> value
            self.key = self.value
            self.value = ''
            return
        
        #
        # Convert various elements or values to native values.
        #
        if name == 'true':
            self.value = True
        elif name == 'false':
            self.value = False
        elif name == 'integer':
            self.value = int( self.value )
        elif name in ( 'array', 'dict' ):

            #
            # Container closed. Pop stack to get back previous container
            #
            self.container, self.stack = self.stack
            self.value = ''
            return

        #
        # Insert value into current open container if there is one.
        #
        if self.container is not None:
            if self.key is not None:
                self.container[ self.key ] = self.value
                self.key = None
            else:
                if isinstance( self.container, list ):
                    self.container.append( self.value )

        self.value = ''

    #
    # XML parsing hook invoked for text data between start and end element
    # tags. May be called multiple times for the same tag, so accumulate the
    # results.
    #
    def characterData( self, data ):
        self.value += data

    def getTracks( self ): return self.container[ 'Tracks' ]
    def getPlaylists( self ): return self.container[ 'Playlists' ]

#
# Collection of containers of iTune artists, albums, playlists, etc. Maintains
# an AppleScript connection with an iTunes server
# XML element object that describes the track.
#
class iTunesXML( object ):

    #
    # The minimum amount of time that must elapse before we will reload the
    # iTunes XML file.
    #
    kLibraryReloadInterval = 60 * 5 # 5 minutes
    
    #
    # The name of the playlist we use for playback
    #
    kOurPlaylistName = 'MBJB'

    #
    # Transitions from one repeat mode to the next.
    #
    kRepeatTransitions = { appscript.k.off: appscript.k.all,
                           appscript.k.all: appscript.k.one,
                           appscript.k.one: appscript.k.off }

    def __init__( self ):

        #
        # Get the location of the iTunes XML file. Apparently we can get it
        # from the MacOS X defaults database. Look ma! No error checking!
        #
        pipe = subprocess.Popen( ['defaults', 'read', 'com.apple.iapps',
                                  'iTunesRecentDatabases' ], 
                                 stdout = subprocess.PIPE )
        content = pipe.communicate()[ 0 ]
        lines = content.split()
        location = eval( lines[ 1 ] )

        #
        # Convert the (file:) URL from above into a local file path.
        #
        self.xmlFilePath, headers = urllib.urlretrieve( location )
        self.backgroundLoader = None
        self.loadedTimeStamp = None

        #
        # Establish an AppleScript connection to the iTunes application
        #
        self.lastTrack = None

        #
        # Initialize iTunes containers
        #
        self.artistMap = {}     # Mapping of names to Artist objects
        self.artistList = []    # List of all Artist objects
        self.albumList = []     # List of all Album objects
        self.genreMap = {}      # Mapping of genre names to a list of Albums
        self.genreNames = []    # Found genre names
        self.playlistNames = [] # Names of the playlists found in iTunes

    def reloadCheck( self ):

        #
        # See if the modified timestamp of the XML file is later than the time
        # stamp of the last load. If not, don't continue.
        #
        when = datetime.fromtimestamp( stat( self.xmlFilePath )[ ST_MTIME ] )
        if when <= self.loadedTimeStamp:
            return

        #
        # Only reload if kLibraryReloadInterval seconds has passed since the
        # last reload.
        #
        delta = datetime.now() - self.loadedTimeStamp
        if delta.seconds < self.kLibraryReloadInterval:
            return

        #
        # See if we have a background thread running. If so, don't continue.
        #
        if self.backgroundLoader:
            if self.backgroundLoader.isAlive():
                return

            #
            # Reap the thread.
            #
            self.backgroundLoader.join()

        #
        # Create a background loader thread and start it.
        #
        self.backgroundLoader = threading.Thread( target = self.load )
        self.backgroundLoader.start()

    #
    # Obtain an AppleScript object that refers to the iTunes application
    #
    def getApp( self ): return appscript.app( 'iTunes' )

    #
    # Obtain an AppleScript object that refers to the main iTunes library.
    # *** FIXME: make universal. I think this is only valid for US or
    # English-speaking countries.
    #
    def getLibrary( self ): return self.getApp().library_playlists[ 'Library' ]

    #
    # Load the iTunes XML file at a given path.
    #
    def load( self ):

        print( '... loading XML file', self.xmlFilePath )
        startTime = datetime.now()

        parser = XMLParser( self.xmlFilePath )
        rawTracks = parser.getTracks()

        tracks = {}
        artistMap = {}
        artistList = []
        albumList = []
        genreMap = {}

        #
        # Visit all of the tracks found in the 'Tracks' <dict>
        #
        for track in rawTracks.values():

            #
            # For now, we only work with audio files.
            #
            trackType = track.get( 'Track Type' )
            if trackType != 'File':
                continue

            kind = track.get( 'Kind', '' )
            if not kind.endswith( 'audio file' ):
                continue

            #
            # By default we use the 'album artist' tag instead of 'artist' so
            # that collections of various artists remain together
            #
            artistName = track.get( 'Album Artist', '' )
            if not artistName:
                if track.get( 'Compilation', 0 ):
                    artistName = 'Various Artists'
                else:
                    artistName = track.get( 'Artist', '' )
            if not artistName:
                continue

            artistName = OrderedItem( artistName )

            #
            # Get the album name
            #
            albumName = track.get( 'Album', '' )
            if not albumName:
                continue

            #
            # Locate an existing Artist object for the artist name. Create new
            # one if necessary and install.
            #
            artist = artistMap.get( artistName )
            if artist is None:
                artist = Artist( artistName )
                artistMap[ artistName ] = artist
                artistList.append( artist )

            #
            # Locate an existing album for the album name. Look first inside
            # the artist.
            #
            albumName = OrderedItem( albumName )
            album = None
            if len( artist.albums ):
                for index in range( artist.getAlbumCount() - 1, -1, -1 ):
                    album = artist.getAlbum( index )
                    if album == albumName:
                        break
                if album != albumName:
                    album = None

            #
            # If not found, create a new one and install.
            #
            if album is None:
                album = Album( artist, albumName )
                artist.addAlbum( album )
                albumList.append( album )

                #
                # Update the genre names
                #
                genreName = track.get( 'Genre' )
                if genreName is not None and len( genreName ) > 0:
                    genreName = OrderedItem( genreName )
                    genreList = genreMap.get( genreName )
                    if genreList is None:
                        genreMap[ genreName ] = genreList = []
                    genreList.append( album )

            #
            # If the 'Artist' field is different than 'Album Artist', link the
            # album to the an entry for the 'Artist'.
            #
            aliasName = track.get( 'Artist' )
            if aliasName and aliasName != artistName.getName():
                aliasName = OrderedItem( aliasName )
                alias = artistMap.get( aliasName )
                if alias is None:
                    alias = Artist( aliasName )
                    artistMap[ aliasName ] = alias
                    artistList.append( alias )
                found = None
                for index in range( alias.getAlbumCount() ):
                    tmp = alias.getAlbum( index )
                    if tmp == albumName:
                        found = tmp
                        break
                if found is None:
                    alias.addAlbum( album )

            #
            # Add the track to the album. Place it under its persistent ID as
            # well as its track ID. The former is more stable, while the latter
            # is still used for playlists.
            #
            track = Track( track )
            tracks[ track.getID() ] = track
            tracks[ track.track.get( 'Track ID' ) ] = track
            album.addTrack( track )

        #
        # Done processing the tracks. Sort the artists and albums by their
        # keys.
        #
        artistList.sort()
        albumList.sort()

        #
        # Validate the load.
        #
        if 0:
            library = self.getLibrary()
            print( '...validating loaded track IDs' )
            for artist in artistList:
                for album in artist.getAlbums():
                    for track in album.getTracks():
                        if library.tracks[ appscript.its.persistent_ID ==
                                           track.getID() ].name()[0] != \
                                           track.getName():
                            print( '*** track ID mismatch', track.getID(),
                                   track.getName() )

        #
        # Now install the new data structures.
        #
        self.artistMap = artistMap
        self.artistList = artistList
        self.albumList = albumList

        #
        # Obtain a sorted list of genre names.
        #
        genreNames = genreMap.keys()
        genreNames.sort()

        self.genreMap = genreMap
        self.genreNames = genreNames

        #
        # Create Playlist objects to represent meaningful playlists.
        #
        playlistList = []
        for each in parser.getPlaylists():
            if each.get( 'Master', False ): continue
            if each.get( 'Folder', False ): continue
            items = each.get( 'Playlist Items', [] )
            if len( items ) == 0: continue
            playlist = Playlist( each.get( 'Name' ) )
            for item in items:
                trackId = item[ 'Track ID' ]
                track = tracks.get( trackId )
                if track:
                    playlist.tracks.append( track )
            if playlist.getTrackCount() > 0:
                playlistList.append( playlist )

        playlistList.sort()
        self.playlistList = playlistList

        self.loadedTimeStamp = datetime.now()
        duration = self.loadedTimeStamp - startTime

        print( '... finished in', duration.seconds, 'seconds' )

    def getGenreNames( self ): return self.genreNames
    def getGenreCount( self ): return len( self.genreNames )

    #
    # Obtain the list of albums associated with a genre. Accept either index or
    # genre name.
    #
    def getGenre( self, key ):
        if type( key ) is type( 0 ):
            key = self.genreNames[ key ]
        return self.genreMap[ key ]

    def getPlaylistList( self ): return self.playlistList
    def getPlaylistCount( self ): return len( self.playlistList )
    def getPlaylist( self, key ):
        if type( key ) is type( 0 ):
            playlist = self.playlistList[ key ]
        else:
            key = OrderedItem( key )
            pos = bisect_left( self.playlistList, key )
            playlist = self.playlistList[ pos ]
            if playlist != key:
                playlist = None
        return playlist

    def getArtistList( self ): return self.artistList
    def getArtistCount( self ): return len( self.artistList )

    #
    # Obtain the artist for a given key value. Accept either index or artist
    # name.
    #
    def getArtist( self, key ):
        if type( key ) is type( 0 ):
            artist = self.artistList[ key ]
        else:
            key = OrderedItem( key )
            artist = self.artistMap.get( key.getKey() )
        return artist

    def getAlbumList( self ): return self.albumList
    def getAlbumCount( self ): return len( self.albumList )
    
    #
    # Obtain the album for a given key value. Accept either index or album
    # name.
    #
    def getAlbum( self, key ):
        if type( key ) is type( 0 ):
            album = self.albumList[ key ]
        else:
            
            #
            # We don't maintain a mapping of album names to album artists. Use
            # binary search on the sorted list of albums to find a match.
            #
            key = OrderedItem( key )
            pos = bisect_left( self.albumList, key )
            album = self.albumList[ pos ]
            if album != key:
                album = None
        return album

    #
    # Scan the list of albums for those matching a given search term.
    #
    def searchForAlbum( self, term ):
        return self.searchFor( term, self.albumList )

    #
    # Scan the list of artists for those matching a given search term.
    #
    def searchForArtist( self, term ):
        return self.searchFor( term, self.artistList )

    #
    # Scan a container for elements containing a given search term.
    #
    def searchFor( self, term, container ):
        term = term.upper()
        found = []
        for each in container:
            if each.key.find( term ) != -1:
                found.append( each )
        return found

    #
    # Application volume controls. NOTE: for some reason unable to change
    # iTunes volume by delta of 1.
    #
    def getVolume( self ): 
        value = int( self.getApp().sound_volume.get() )
        return value

    def setVolume( self, value ):
        self.getApp().sound_volume.set( value )

    def adjustVolume( self, delta ): 
        adjustment = delta
        old = self.getVolume()
        if ( old == 0 and delta < 0 ) or ( old == 100 and delta > 0 ):
            return
        while old == self.getVolume():
            self.setVolume( old + delta )
            delta += adjustment

    #
    # Application mute controls.
    #
    def getMute( self ): return self.getApp().mute.get()
    def setMute( self, value ): self.getApp().mute.set( value )
    def toggleMute( self ): self.setMute( not self.getMute() )

    #
    # Playlist shuffle controls.
    #
    def getShuffle( self ): 
        return self.getActivePlaylistObject().shuffle.get()
    def setShuffle( self, value ): 
        self.getActivePlaylistObject().shuffle.set( value )
    def toggleShuffle( self ): 
        self.setShuffle( not self.getShuffle() )

    #
    # Playlist repeat controls. The valid values for 'value' are: 
    #  - appscript.k.off
    #  - appscript.k.all
    #  - appscript.k.one
    #
    def getRepeat( self ): 
        return self.getActivePlaylistObject().song_repeat.get()
    def setRepeat( self, value ): 
        return self.getActivePlaylistObject().song_repeat.set( value )
    def toggleRepeat( self ):
        self.setRepeat( self.kRepeatTransitions[ self.getRepeat() ] )

    #
    # Get the current playlist. If there is not one, then use our playlist
    # (MBJB)
    #
    def getActivePlaylistObject( self ):
        try:
            return self.getApp().current_playlist.get()
        except appscript.reference.CommandError:
            pass
        return self.getPlaylistObject( self.kOurPlaylistName, True )

    def getActivePlaylistSize( self ):
        return len( self.getActivePlaylistObject().tracks() )

    #
    # Obtain current track. If there is not one, then return the last track
    # that was seen.
    #
    def getCurrentTrack( self ):
        try:
            track = ActiveTrack( self.getApp().current_track.get() )
            self.lastTrack = track
        except appscript.reference.CommandError:
            track = self.lastTrack
        return track

    #
    # Determine if iTunes is currently playing
    #
    def isPlaying( self ): return self.getPlayerState() == 'k.playing'

    #
    # Determine if iTunes is currently paused
    #
    def isPaused( self ): return self.getPlayerState() == 'k.paused'

    #
    # Get the current state of the iTunes player (playing, paused, stopped )
    #
    def getPlayerState( self ): return str( self.getApp().player_state.get() )
    
    #
    # Get the current position (seconds) of the iTunes player
    #
    def getPlayerPosition( self ): 
        try:
            return int( self.getApp().player_position.get() )
        except TypeError:
            return 0

    #
    # Stop the iTunes player
    #
    def stop( self ): self.getApp().stop()
    
    #
    # Start the iTunes player at the beginning of the current track
    #
    def play( self ): self.getApp().play()
    
    #
    # Pause the iTunes player
    #
    def pause( self ): self.getApp().pause()

    #
    # Move the player to the beginning of the current track.
    #
    def beginTrack( self ): self.getApp().back_track()

    #
    # Move the player to the previous track in the playlist
    #
    def previousTrack( self ): self.getApp().previous_track()
    
    #
    # Move the player to the next track in the playlist
    #
    def nextTrack( self ): self.getApp().next_track()
    
    #
    # Move the player backwards over the current track
    #
    def rewind( self ): self.getApp().rewind()

    #
    # Move the player fast-forward over the current track
    #
    def fastForward( self ): self.getApp().fast_forward()
    
    #
    # Resume normal playback of the current track (after rewind() or
    # fastForward())
    #
    def resume( self ): self.getApp().resume()

    #
    # Get the AppleScript object representing the named playlist. If the
    # playlist does not exist, create it if allowed
    #
    def getPlaylistObject( self, name, create = True ):
        playlist = None
        try:
            playlist = self.getApp().user_playlists[ name ].get()
        except appscript.reference.CommandError:
            pass

        if playlist is None and create:
            playlist = self.getApp().make( 
                new = appscript.k.user_playlist,
                with_properties = { appscript.k.name: name } )

        #
        # Make playlist current if it exists
        #
        if playlist:
            self.getApp().browser_windows.get()[ 0 ].view.set( playlist )
        return playlist

    #
    # Remove tracks for a given playlist
    #
    def playlistClear( self, playlist ):
        self.getApp().stop()
        playlist.tracks.delete()

    #
    # Add a track to a playlist
    #
    def playlistAddTrack( self, playlist, track ):
        self.getLibrary().tracks[ 
            appscript.its.persistent_ID == track.getID() ].duplicate(
            to = playlist )

    #
    # Add a the tracks of an album to a playlist
    #
    def playlistAddAlbum( self, playlist, album ):
        for track in album.getTracks():
            self.playlistAddTrack( playlist, track )

    def doPlayPlaylist( self, playlist, trackIndex ):
        if playlist is None:
            print( '*** NULL playlist' )
        elif trackIndex >= len( playlist.tracks.get() ):
            print( '*** invalid trackIndex:', trackIndex,
                   len( playlist.tracks.get() ) )
        else:
            playlist.tracks[ trackIndex + 1 ].play()

    def playPlaylist( self, playlist, trackIndex = 0 ):
        playlist = self.getPlaylistObject( playlist.getName(), False )
        self.doPlayPlaylist( playlist, trackIndex )

    #
    # Clear the 'MBJB' playlist, add the tracks of the albums of the given
    # artist to the playlist and commence playback.
    #
    def playArtist( self, artist ):
        playlist = self.getPlaylistObject( self.kOurPlaylistName, True )
        self.playlistClear( playlist )
        for each in artist.getAlbums():
            self.playlistAddAlbum( playlist, each )
        self.doPlayPlaylist( playlist, 1 )

    #
    # Clear the 'MBJB' playlist, add the tracks of the given album to the
    # playlist and commence playback.
    #
    def playAlbum( self, album, trackIndex = 0 ):
        playlist = self.getPlaylistObject( self.kOurPlaylistName, True )
        self.playlistClear( playlist )
        self.playlistAddAlbum( playlist, album )
        self.doPlayPlaylist( playlist, trackIndex )

    #
    # Obtain the current rating for the given album.
    #
    def getAlbumRating( self, album ):
        track = album.getTrack( 0 )
        id = track.getID()
        track = self.getLibrary().tracks[ 
            appscript.its.persistent_ID == id ].get()[ 0 ]
        rating = track.album_rating.get()
        ratingKind = track.album_rating_kind.get()
        
        #
        # If the user's album rating is 0, iTunes may return to us a computed
        # value based on ratings of the album's tracks. We want to ignore such
        # a rating for our purposes.
        #
        if repr( ratingKind ) == 'k.computed':
            rating = 0
        return rating

    #
    # Set a new rating for the given album.
    #
    def setAlbumRating( self, album, rating ):
        id = album.getTrack( 0 ).getID()
        self.getLibrary().tracks[ 
            appscript.its.persistent_ID == id ].album_rating.set( rating )

    #
    # Obtain the current rating for the given track AND the current rating for
    # the track's album
    #
    def getTrackRating( self, track ):
        id = track.getID()
        track = self.getLibrary().tracks[ 
            appscript.its.persistent_ID == id ].get()[ 0 ]
        rating = track.rating.get()
        ratingKind = track.rating_kind.get()

        #
        # If the user's track rating is 0, iTunes may return to us the rating
        # value assigned to the track's album. We want to ignore such a rating
        # for our purposes.
        #
        if repr( ratingKind ) == 'k.computed':
            rating = 0
        albumRating = track.album_rating.get()
        return rating, albumRating

    #
    # Set a new rating for the given track
    #
    def setTrackRating( self, track, rating ):
        id = track.getID()
        self.getLibrary().tracks[ 
            appscript.its.persistent_ID == id ].rating.set( rating )

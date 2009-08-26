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
# Obtain an AppleScript object that refers to the iTunes application
#
def GetApp(): 
    return appscript.app( 'iTunes' )

#
# Obtain an AppleScript object that refers to the main iTunes library.
# *** FIXME: make universal. I think this is only valid for US or
# English-speaking countries.
#
def GetLibrary(): 
    return GetApp().library_playlists[ 'Library' ]

#
# Class for an artist. Maintains a list of albums associated with the artist.
#
class Artist( OrderedItem ):

    #
    # Constructor. NAME is the name of the artist as found in the XML file.
    #
    def __init__( self, name ):
        OrderedItem.__init__( self, name )
        self.albums = []
        self.needSort = False

    #
    # Add an Album object to the list of albums for this artist
    #
    def addAlbum( self, album ): 
        self.needSort = True
        self.albums.append( album )

    #
    # Get the list of albums associated with this artist
    #
    def getAlbums( self ):
        if self.needSort:
            self.albums.sort()
            self.needSort = False
        return self.albums

    #
    # Obtain the number of albums associated with this artist 
    #
    def getAlbumCount( self ): return len( self.albums )
    
    #
    # Get the Album object at INDEX.
    #
    def getAlbum( self, index ): return self.getAlbums()[ index ]

    #
    # Add all of the albums associate with this artist to the PLAYLIST
    # playlist.
    #
    def addToPlaylist( self, playlist ):
        for album in self.getAlbums():
            album.addToPlaylist( playlist )

    def __repr__( self ): return 'Artist "%s"' % ( self.getName(), )

#
# Class for an 'album' created by an artist. Maintains a list of tracks that
# make up the album.
#
class Album( OrderedItem ):

    #
    # Constructor. ARTIST is an Artist object associated with the album, NAME
    # is the name of the album from the XML file.
    #
    def __init__( self, artist, name ):
        OrderedItem.__init__( self, name )
        self.artist = artist
        self.tracks = []

        #
        # Since tracks may arrive in any order in the XML file, we will sort
        # them before returning any. The Track class defines the order as the
        # track index from the album. An alternative way would be to
        # preallocate an array and place tracks at their appropriate index.
        # However, this could leave holes in the array due to missing tracks.
        # This method, though slower for the first access, will not reveal gaps
        # in the tracks.
        #
        self.needSort = True 

    #
    # Add a Track object to the list of tracks for this album
    #
    def addTrack( self, track ):
        self.needSort = True
        self.tracks.append( track )

    #
    # Obtain the name of the artist associated with this album
    #
    def getArtistName( self ): return self.artist.getName()

    #
    # Obtain the list of Track objects associated with this album
    #
    def getTracks( self ): 
        if self.needSort:
            
            #
            # Since the Track object define ordering by their index within the
            # original album, this will place them in their proper track order.
            #
            self.tracks.sort()
            self.needSort = False
        return self.tracks

    #
    # Obtain the number of tracks associated with this album
    #
    def getTrackCount( self ): return len( self.tracks )

    #
    # Get the Track object at INDEX
    #
    def getTrack( self, index ): return self.getTracks()[ index ]

    #
    # Add the tracks associated with this album to the playlist PLAYLIST
    #
    def addToPlaylist( self, playlist ):
        for track in self.getTracks():
            track.addToPlaylist( playlist )

    def __repr__( self ): return 'Album "%s"' % ( self.getName(), )

#
# Class for a playlist in iTunes. A playlist contains a list of tracks as well
# as an AppleScript refernce to the internal iTunes playlist object it
# represents.
#
class Playlist( OrderedItem ):

    #
    # Constructor. PLAYLISTOBJECT is the iTunes playlist AppleScript object to
    # mirror, NAME is the playlist name, and CANMANIPULATE is a boolean flag
    # indicating whether the user may manipulate the contents of the playlist
    # (including deleting it)
    #
    def __init__( self, playlistObject, name, canManipulate ):
        OrderedItem.__init__( self, name )
        self.playlistObject = playlistObject
        self.canManipulate = canManipulate
        self.tracks = []

    #
    # Obtain the list of Track objects associated with this playlist
    #
    def getTracks( self ): return self.tracks

    #
    # Obtain the number of tracks associated with this playlist
    #
    def getTrackCount( self ): return len( self.tracks )

    #
    # Obtain the Track object at INDEX
    #
    def getTrack( self, index ): return self.tracks[ index ]

    #
    # Determine if the user can manipulate this playlist
    #
    def getCanManipulate( self ): return self.canManipulate

    #
    # Clear the tracks from this playlist
    #
    def clear( self ):
        if not self.getCanManipulate():
            return

        #
        # Attempt to keep our track list and iTunes in sync.
        #
        try:
            self.playlistObject.tracks.delete()
            self.tracks = []
        except appscript.reference.CommandError:
            print( '*** failed to clear playlist', self.getName() )
            pass

    #
    # Add a Track object to this playlist.
    #
    def addTrack( self, track ):
        
        #
        # Attempt to keep our track list and iTunes in sync.
        #
        try:
            GetLibrary().tracks[ 
                appscript.its.persistent_ID == track.getID() ].duplicate(
                to = self.playlistObject )
            self.tracks.append( track )
        except appscript.reference.CommandError:
            print( '*** failed to add track', track.getName(), 'to playlist',
                   self.getName() )
            pass

    #
    # Ask iTunes to begin playing this playlist
    #
    def play( self, trackIndex = 0 ):
        if trackIndex >= self.getTrackCount():
            print( '*** invalid trackIndex:', trackIndex )
        else:
            try:
                self.playlistObject.tracks[ trackIndex + 1 ].play()
            except appscript.reference.CommandError:
                print( '*** failed to start playing playlist', self.getName(),
                       'at track', trackIndex )
            pass

    #
    # Get the current shuffle setting for this playlist
    #
    def getShuffle( self ): 
        return self.playlistObject.shuffle.get()

    #
    # Change the shuffle setting for this playlist
    #
    def setShuffle( self, value ): 
        self.playlistObject.shuffle.set( value )

    #
    # Get the current repeat mode for this playlist
    #
    def getRepeat( self ): 
        return self.playlistObject.song_repeat.get()

    #
    # Change the repeat mode for this playlist
    #
    def setRepeat( self, value ): 
        self.playlistObject.song_repeat.set( value )

    def __repr__( self ): return 'Playlist "%s"' % ( self.getName(), )

#
# Class for a track of an album of an artist. Contains the original iTunes XML
# element object that describes the track. NOTE: defines ordering and hashing
# methods to properly order a collection of Track objects by their track index.
#
class Track( OrderedItem ):

    #
    # Constructor. TRACK is either a Python dictionary containing the
    # attributes found in the XML file for this track, or it is an AppleScript
    # iTunes track object.
    #
    def __init__( self, track ):
        if isinstance( track, dict ):
            OrderedItem.__init__( self, track.get( 'Name', '' ) )
            self.id = str( track.get( 'Persistent ID' ) )
            self.trackId = track.get( 'Track ID' )
            self.index = int( track.get( 'Track Number', '-1' ) )
            self.artistName = track.get( 'Artist', '' )
            self.albumName = track.get( 'Album', '' )
            self.duration = int( track.get( 'Total Time', 0 ) ) / 1000
        else:
            OrderedItem.__init__( self, track.name() )
            self.id = track.persistent_ID()
            self.trackId = None # !!!
            self.index = track.track_number()
            self.artistName = track.artist()
            self.albumName = track.album()
            self.duration = track.duration()

    #
    # Obtain the persistent ID for this track.
    #
    def getID( self ): return self.id

    #
    # Obtain the track ID for this track. NOTE: this is only valid (apparently)
    # for playlist relationships.
    #
    def getTrackId( self ): return self.trackId

    #
    # Obtain the index of this track. This determines the ordering of the track
    # in the parent Album object in which it resides.
    #
    def getIndex( self ): return self.index

    #
    # Obtain the name of this track
    #
    def getName( self ): return self.name

    #
    # Obtain the artist name for this track
    #
    def getArtistName( self ): return self.artistName

    #
    # Obtain the album name for this track
    #
    def getAlbumName( self ): return self.albumName

    #
    # Obtain the duration in seconds for this track
    #
    def getDuration( self ): return self.duration

    #
    # Add the track to the PLAYLIST playlist
    #
    def addToPlaylist( self, playlist ):
        playlist.addTrack( self )

    #
    # Define a comparison method for Track objects such that they will be
    # ordered by their track index values.
    #
    def __cmp__( self, other ): return cmp( self.index, other.index )

    def __repr__( self ): return 'Track "%d - %s"' % ( self.index, self.name, )

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

    #
    # Constructor.
    #
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

    #
    # See if we should reload the iTunes XML file. If so, we do it in a
    # separate thread.
    #
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
    # Load the iTunes XML file. NOTE: this may execute in a separate thread, so
    # we keep all collections local until the very end, where we install them
    # as the new values.
    #
    def load( self ):

        print( '... loading XML file', self.xmlFilePath )
        startTime = datetime.now()

        #
        # Create an XML parser and parse the file.
        #
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
            # the artist. NOTE: do not use the getter methods to fetch albums,
            # since we do not want to cause a sort on the held albums yet.
            #
            albumName = OrderedItem( albumName )
            album = None
            if len( artist.albums ):
                for index in range( artist.getAlbumCount() - 1, -1, -1 ):
                    album = artist.albums[ index ]
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
                
                #
                # NOTE: do not use the getter methods to fetch albums, since we
                # do not want to cause a sort on the held albums yet.
                #
                for index in range( alias.getAlbumCount() ):
                    tmp = alias.albums[ index ]
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
            tracks[ track.getTrackId() ] = track
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
            library = GetLibrary()
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
            
            #
            # Playlists to ignore
            #
            if each.get( 'Master', False ): continue
            if each.get( 'Folder', False ): continue

            #
            # Obtain the iTunes playlist object with the same name
            #
            name = each.get( 'Name' )
            playlistObject = GetApp().user_playlists[ name ].get()

            #
            # Determine if this playlist is one that the user may manipulate.
            #
            canManipulate = True
            if each.get( 'Smart Info', False ): canManipulate = False
            if each.get( 'Distinguished Kind', False ): canManipulate = False

            #
            # Create a new Playlist object and add Track objects to it.
            #
            playlist = Playlist( playlistObject, name, canManipulate )
            playlistList.append( playlist )

            items = each.get( 'Playlist Items', [] )
            for item in items:
                
                #
                # NOTE: playlists references tracks by its 'Track ID' element,
                # not by their 'Persistent ID' element.
                #
                trackId = item[ 'Track ID' ]
                track = tracks.get( trackId )
                
                #
                # This should always be true...
                #
                if track:
                    playlist.tracks.append( track )

        #
        # Order the available playlists and install
        #
        playlistList.sort()
        self.playlistList = playlistList

        #
        # Update the loaded timestamp so we can detect when the XML file
        # changes in the future.
        #
        self.loadedTimeStamp = datetime.now()
        duration = self.loadedTimeStamp - startTime

        print( '... finished in', duration.seconds, 'seconds' )

    #
    # Obtain the names of the genres in the iTunes library, as found during the
    # last XML load.
    #
    def getGenreNames( self ): return self.genreNames
    
    #
    # Obtain the number of genres in the iTunes library
    #
    def getGenreCount( self ): return len( self.genreNames )

    #
    # Obtain the list of albums associated with a genre, where KEY may be an
    # ingteger index or a string name.
    #
    def getGenre( self, key ):
        if type( key ) is type( 0 ):
            key = self.genreNames[ key ]
        return self.genreMap[ key ]

    #
    # Get the list of playlists in the iTunes library, as found during the last
    # XML load.
    #
    def getPlaylistList( self ): return self.playlistList
    
    #
    # Obtain the number of playlists in the iTunes library
    #
    def getPlaylistCount( self ): return len( self.playlistList )
    
    #
    # Obtain the Playlist object for a given key, where KEY may be an integer
    # index or a string name. NOTE: may return None
    #
    def getPlaylist( self, key, createIfMissing = False ):
        if isinstance( key, int ):
            playlist = self.playlistList[ key ]
        else:
            
            #
            # If the name is empty, use our default playlist name ('MBJB')
            #
            if key == '':
                key = self.kOurPlaylistName

            #
            # Search the sorted list for the given key name.
            #
            key2 = OrderedItem( key )
            pos = bisect_left( self.playlistList, key2 )
            playlist = self.playlistList[ pos ]
            if playlist != key2:
                playlist = None

        #
        # If not found, but creation is allowed, create it.
        #
        if playlist is None and createIfMissing:
            playlist = self.createPlaylist( key )

        return playlist

    #
    # Create a new playlist in iTunes under the given name NAME. Add to our
    # internal list of playlists and reorder it.
    #
    def createPlaylist( self, name ):
        try:
            playlist = GetApp().make( 
                new = appscript.k.user_playlist,
                with_properties = { appscript.k.name: name } )
            playlist = Playlist( playlist, name, True )
            self.playlistList.append( playlist )
            self.playlistList.sort()
        except appscript.reference.CommandError:
            playlist = None

        return playlist

    #
    # Delete a playlist from iTunes, where PLAYLIST is an Playlist object.
    #
    def deletePlaylist( self, playlist ):
        try:
            GetApp().playlists[ playlist.getName() ].delete()
            self.playlistList.remove( playlist)
        except appscript.reference.CommandError:
            pass

    #
    # Get the list of artists in the iTunes library, as found during the last
    # XML load.
    #
    def getArtistList( self ): return self.artistList
    
    #
    # Obtain the number of artists in the iTunes library
    #
    def getArtistCount( self ): return len( self.artistList )

    #
    # Obtain the Artist object for a given key, where KEY may be an integer
    # index, an OrderedItem instance, or a string value. NOTE; may return None
    #
    def getArtist( self, key ):
        if isinstance( key, int ):
            artist = self.artistList[ key ]
        else:
            
            #
            # If not an OrderedItem instance, make it one.
            #
            if not isinstance( key, OrderedItem ):
                key = OrderedItem( key )

            artist = self.artistMap.get( key )
        return artist

    #
    # Get the list of albums in the iTunes library, as found during the last
    # XML load.
    #
    def getAlbumList( self ): return self.albumList

    #
    # Obtain the number of albums in the iTunes library
    #
    def getAlbumCount( self ): return len( self.albumList )

    #
    # Obtain the Album object for a given key. where KEY may be an integer
    # index, an OrderedItem instance, or a string value. NOTE: may return None
    #
    def getAlbum( self, key ):
        if isinstance( key, int ):
            album = self.albumList[ key ]
        else:

            #
            # We don't maintain a mapping of album names to album artists. Use
            # binary search on the sorted list of albums to find a match.
            #
            if not isinstance( key, OrderedItem ):
                key = OrderedItem( key )
            pos = bisect_left( self.albumList, key )
            album = self.albumList[ pos ]
            if album != key:
                album = None
        return album

    #
    # Obtain a list of Album objects matching a given search term.
    #
    def searchForAlbum( self, term ):
        return self.searchFor( self.albumList, term )

    #
    # Obtain a list of Artist objects for those matching a given search term.
    #
    def searchForArtist( self, term ):
        return self.searchFor( self.artistList, term )

    #
    # Scan a container for elements containing a given search term, returning a
    # list of matches.
    #
    def searchFor( self, container, term ):
        term = term.upper()
        found = []
        for each in container:
            if each.key.find( term ) != -1:
                found.append( each )
        return found

    #
    # Obtain the current iTunes volume setting.
    #
    def getVolume( self ): 
        return int( GetApp().sound_volume.get() )

    #
    # Change the iTunes volume settiing, where VALUE is an integer from 0 to
    # 100.
    #
    def setVolume( self, value ):
        GetApp().sound_volume.set( value )

    #
    # Adjust the volume by a given DELTA value.
    #
    def adjustVolume( self, delta ): 
        adjustment = delta
        old = self.getVolume()
        if ( old == 0 and delta < 0 ) or ( old == 100 and delta > 0 ):
            return

        #
        # NOTE: some changes in volume apparently do not work. So, we add
        # multiples of DELTA until the volume from iTunes indicates a change.
        #
        while old == self.getVolume():
            self.setVolume( old + delta )
            delta += adjustment

    #
    # Obtain the current iTunes mute setting.
    #
    def getMute( self ): return GetApp().mute.get()

    #
    # Change the iTunes mute setting, where VALUE is 1 or 0
    #
    def setMute( self, value ): GetApp().mute.set( value )

    #
    # Toggle the iTunes mute setting.
    #
    def toggleMute( self ): self.setMute( not self.getMute() )

    #
    # Get the current playlist. If there is not one, then use our playlist
    # (MBJB). This allows us to show what the user is playing via iTunes (or
    # the Remote iPhone application). Returns a Playlist object
    #
    def getActivePlaylist( self ):
        try:
            name = GetApp().current_playlist.name.get()
        except appscript.reference.CommandError:
            name = self.kOurPlaylistName
        return self.getPlaylist( name, True )

    #
    # Get the shuffle setting for the active playlist.
    #
    def getShuffle( self ): 
        return self.getActivePlaylist().geShuffle()
    
    #
    # Set the shuffle setting for the active playlist
    #
    def setShuffle( self, value ): 
        self.getActivePlaylist().setShuffle( value )

    #
    # Toggle the shuffle setting for the active playlist
    #
    def toggleShuffle( self ): 
        self.setShuffle( not self.getShuffle() )

    #
    # Get the current repeat mode for the active playlist
    #
    def getRepeat( self ): 
        return self.getActivePlaylist().getRepeat()
    #
    # Set the repeat mode for the active playlist, where VALUE is one of
    #  - appscript.k.off
    #  - appscript.k.all
    #  - appscript.k.one
    #
    def setRepeat( self, value ): 
        self.getActivePlaylist().setRepeat( value )

    #
    # Change the repeat mode of the active playlist to the next value in the
    # cycle ( appscript.k.off, appscript.k.all, appscript.k.one )
    #
    def toggleRepeat( self ):
        self.setRepeat( self.kRepeatTransitions[ self.getRepeat() ] )

    #
    # Obtain current track. If there is not one, then return the last track
    # that was seen.
    #
    def getCurrentTrack( self ):
        try:
            track = Track( GetApp().current_track.get() )
            self.lastTrack = track
        except appscript.reference.CommandError:
            track = self.lastTrack
        return track

    #
    # Get the current state of the iTunes player (playing, paused, stopped )
    #
    def getPlayerState( self ): return str( GetApp().player_state.get() )

    #
    # Determine if iTunes is currently playing
    #
    def isPlaying( self ): return self.getPlayerState() == 'k.playing'

    #
    # Determine if iTunes is currently paused
    #
    def isPaused( self ): return self.getPlayerState() == 'k.paused'

    #
    # Get the current position (seconds) of the iTunes player
    #
    def getPlayerPosition( self ): 
        try:
            return int( GetApp().player_position.get() )
        except TypeError:
            return 0

    #
    # Stop the iTunes player
    #
    def stop( self ): GetApp().stop()
    
    #
    # Start the iTunes player at the beginning of the current track
    #
    def play( self ): GetApp().play()
    
    #
    # Clear the 'MBJB' playlist, add the Track object(s) of the given OBJECT
    # object to the PLAYLIST playlist and commence playback at the indicated
    # track
    #
    def playObject( self, object, trackIndex = 0 ):
        playlist = self.getPlaylist( self.kOurPlaylistName, True )
        playlist.clear()

        #
        # Ask the object to add its Track objects to the MBJB playlist
        #
        object.addToPlaylist( playlist )
        playlist.play( trackIndex )

    #
    # Pause the iTunes player
    #
    def pause( self ): GetApp().pause()

    #
    # Move the player to the beginning of the current track.
    #
    def beginTrack( self ): GetApp().back_track()

    #
    # Move the player to the previous track in the playlist
    #
    def previousTrack( self ): GetApp().previous_track()
    
    #
    # Move the player to the next track in the playlist
    #
    def nextTrack( self ): GetApp().next_track()
    
    #
    # Move the player backwards over the current track
    #
    def rewind( self ): GetApp().rewind()

    #
    # Move the player fast-forward over the current track
    #
    def fastForward( self ): GetApp().fast_forward()
    
    #
    # Resume normal playback of the current track (after rewind() or
    # fastForward())
    #
    def resume( self ): GetApp().resume()

    #
    # Obtain the current rating for the given ALBUM Album object.
    #
    def getAlbumRating( self, album ):

        #
        # Cannot do anything unless the album has at least one track.
        #
        if album.getTrackCount() == 0:
            return 0

        #
        # Get the first track for this album
        #
        track = album.getTrack( 0 )

        #
        # Get the iTunes track object for the first Track object.
        #
        id = track.getID()
        track = GetLibrary().tracks[ 
            appscript.its.persistent_ID == id ].get()[ 0 ]
        
        #
        # Get the rating and its type for the first track
        #
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
    # Set a new rating for the given ALBUM Album object, where RATING is an
    # integer from 0 to 100.
    #
    def setAlbumRating( self, album, rating ):

        #
        # Cannot do anything unless the album has at least one track.
        #
        if album.getTrackCount() == 0:
            return

        id = album.getTrack( 0 ).getID()
        GetLibrary().tracks[ 
            appscript.its.persistent_ID == id ].album_rating.set( rating )

    #
    # Obtain the current rating for the given track AND the current rating for
    # the track's album
    #
    def getTrackRating( self, track ):
        
        #
        # Get the iTunes track object for the given Track object
        #
        id = track.getID()
        track = GetLibrary().tracks[ 
            appscript.its.persistent_ID == id ].get()[ 0 ]

        #
        # Get the rating and its type for the track
        #
        rating = track.rating.get()
        ratingKind = track.rating_kind.get()

        #
        # If the user's track rating is 0, iTunes may return to us the rating
        # value assigned to the track's album. We want to ignore such a rating
        # for our purposes.
        #
        if repr( ratingKind ) == 'k.computed':
            rating = 0

        return rating

    #
    # Set a new rating for the given track
    #
    def setTrackRating( self, track, rating ):
        id = track.getID()
        GetLibrary().tracks[ 
            appscript.its.persistent_ID == id ].rating.set( rating )

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

from datetime import datetime
from os import stat
from stat import *
import array, asyncore, cPickle, socket, struct, subprocess, threading, \
    traceback, urllib
import ClientPersistence, Display, IR, iTunesXML, Timer

#
# Server class that manages Client instances. Handles SLIMP3 protocol messages,
# creating new Client objects when it receives a message from an unknown SLIMP3
# device.
#
class Server( asyncore.dispatcher ):

    kDefaultPort = 3483
    kSaveClientStateInterval = 10 # seconds
    kLoopPollTimeout = 0.010
    kReceiveBufferSize = 256
    kLibraryLoadCheckInterval = 15   # seconds
    kLibraryReloadInterval = 30 * 60 # 30 minutes

    def __init__( self ):
        asyncore.dispatcher.__init__( self )
        self.loader = None
        self.loadTimeStamp = None
        self.clients = ClientPersistence.ClientPersistence()
        self.makeTimerManager()
        self.makeITunesManager()
        self.makeIRManager()
        self.makeDispatcher()

    def makeIRManager( self ):
        self.irManager = IR.IR()

    def makeITunesManager( self ):
        self.iTunes = iTunesXML.iTunesXML()
        self.iTunesLoad()

    def makeTimerManager( self ):
        self.timerManager = Timer.TimerManager()

    def iTunesLoad( self ):
        print "Server.iTunesLoad"

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
        self.filename, headers = urllib.urlretrieve( location )
        self.iTunes.load( self.filename )
        if self.loader:
            self.loader.join()
            self.loader = None
        self.loadTimeStamp = stat( self.filename )[ ST_MTIME ]
        self.loader = None

    def iTunesLoadCheck( self ):
        when = stat( self.filename )[ ST_MTIME ]
        if self.loadTimeStamp is None:
            delta = self.kLibraryReloadInterval
        else:
            delta = when - self.loadTimeStamp
        if delta >= self.kLibraryReloadInterval and self.loader is None:
            self.loader = threading.Thread( target = self.iTunesLoad )
            self.loader.start()
        self.addTimer( self.kLibraryLoadCheckInterval, self.iTunesLoadCheck )

    def makeDispatcher( self, port = kDefaultPort ):
        if self.socket:
            self.close()
            self.socket = None
        self.create_socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socket.bind( ( '', port ) )
        self.set_reuse_addr()

    def run( self ):
        timerManager = self.timerManager
        timerManager.addTimer( self.kSaveClientStateInterval, 
                               self.saveClientState )
        loop = asyncore.loop
        while 1:
            loop( timeout = self.kLoopPollTimeout, use_poll = True, count = 1 )
            timerManager.processTimers()

    def handle_read( self ):
        msg, addr = self.socket.recvfrom( self.kReceiveBufferSize )
        if msg[ 0 ] == 'd':
            self.processDiscovery( addr )
        else:
            self.processMessage( addr, msg )

    def processMessage( self, addr, msg ):
        client = self.clients.getClient( self, addr )
        kind = msg[ 0 ]
        if kind == 'h':
            self.processHello( client )
        elif kind == 'i':
            self.processIRMessage( client, msg )
        else:
            print( 'unknown message type:', kind )

    def processDiscovery( self, addr ):
        self.sendDiscoveryResponse( addr )

    def processHello( self, client ):
        client.touch()

    def processIRMessage( self, client, msg ):
        format = '>cBIBBI6x'
        msgType, zero, timeStamp, remoteId, sigBits, buttonCode = \
            struct.unpack( format, msg )
        remoteId = 0            # !!! FIX ME
        key = self.irManager.lookup( remoteId, buttonCode )
        if key is not None:
            try:
                client.processKeyEvent( timeStamp, key )
            except:
                print '*** failed to process IR message'
                traceback.print_exc()

    def handle_connect( self ): pass
    def handle_accept( self ): pass
    def writable( self ): return False

    def sendHello( self, address ):
        self.socket.sendto( 'h' + chr( 0 ) * 17, address )

    def sendDiscoveryResponse( self, address ):
        self.socket.sendto( 'D' + chr( 0 ) * 17, address )

    def saveClientState( self ):
        self.clients.save()
        self.timerManager.addTimer( self.kSaveClientStateInterval,
                                    self.saveClientState )

    def addTimer( self, delta, notifier ):
        return self.timerManager.addTimer( delta, notifier )

    def removeTimer( self, timer ):
        self.timerManager.removeTimer( timer )

if __name__ == "__main__":
    a = Server()
    a.run()

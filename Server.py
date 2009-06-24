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
import subprocess
import array, asyncore, cPickle, socket, struct, threading, urllib
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

    def __init__( self ):
        asyncore.dispatcher.__init__( self )
        self.clients = ClientPersistence.ClientPersistence()
        self.makeITunesManager()
        self.makeIRManager()
        self.makeTimerManager()
        self.makeDispatcher()

    def makeIRManager( self ):
        self.irManager = IR.IR()

    def makeITunesManager( self ):
        
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
        filename, headers = urllib.urlretrieve( location )

        #
        # Let's hope it works!
        #
        self.iTunes = iTunesXML.iTunesXML()
        self.iTunes.load( filename )

    def makeTimerManager( self ):
        self.timerManager = Timer.TimerManager()

    def makeDispatcher( self, port = kDefaultPort ):
        if self.socket:
            self.close()
            self.socket = None
        self.create_socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socket.bind( ( '', port ) )
        self.set_reuse_addr()

    def run( self ):
        timerManager = self.timerManager
        timerManager.addTimer( self.kSaveClientStateInterval, self, 
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
        # print 'key:', key
        if key is not None:
            client.processKeyEvent( timeStamp, key )

    def handle_connect( self ): pass
    def handle_accept( self ): pass
    def writable( self ): return False

    def sendHello( self, address ):
        try:
            self.socket.sendto( 'h' + chr( 0 ) * 17, address )
            return True
        except:
            return False

    def sendDiscoveryResponse( self, address ):
        try:
            self.socket.sendto( 'D' + chr( 0 ) * 17, address )
            return True
        except:
            return Falsen

    def saveClientState( self ):
        self.clients.save()
        self.timerManager.addTimer( self.kSaveClientStateInterval, self, 
                                    self.saveClientState )

    def addTimer( self, delta, client, notifier ):
        return self.timerManager.addTimer( delta, client, notifier )

    def removeTimer( self, timer ):
        self.timerManager.removeTimer( timer )

if __name__ == "__main__":
    a = Server()
    a.run()

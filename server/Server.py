#
# Copyright (C) 2009, 2010 Brad Howes.
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

from os import stat
from stat import *
import array, asyncore, cPickle, socket, struct, traceback
import ClientPersistence, Display, IR, iTunesXML, Timer

#
# Server class that manages Client instances. Handles SLIMP3 protocol messages,
# creating new Client objects when it receives a message from an unknown SLIMP3
# device.
#
class Server( asyncore.dispatcher ):

    kDefaultPort = 3483
    kSaveClientStateInterval = 10 # seconds
    kLoopPollTimeout = 0.010      # Maximum amount of time to give to asyncore
    kReceiveBufferSize = 2048     # 2K should be enough for everyone...
    kLibraryLoadCheckInterval = 15 # seconds

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
        self.iTunes.load()
        self.addTimer( self.kLibraryLoadCheckInterval, self.reloadCheck )

    def reloadCheck( self ):
        self.iTunes.reloadCheck()
        self.addTimer( self.kLibraryLoadCheckInterval, self.reloadCheck )

    def makeTimerManager( self ):
        self.timerManager = Timer.TimerManager()

    def makeDispatcher( self, port = kDefaultPort ):
        if self.socket:
            self.close()
            self.socket = None
        self.create_socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socket.bind( ( '', port ) )
        self.socket.setblocking( 0 )
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
        
        #
        # Data available on our server socket. Keep reading until there isn't
        # any.
        #
        keyAddr = None
        keyMsg = None
        while 1:
            try:
                msg, addr = self.socket.recvfrom( self.kReceiveBufferSize )
            except socket.error:
                break

            #
            # Delay key messages until we read the last one. This assumes we
            # process incoming messages faster than they arrive. Otherwise, we
            # will end up doing nothing ...
            #
            kind = msg[ 0 ]
            if kind == 'd':
                self.processDiscovery( addr )
            elif kind == 'i':
                keyAddr = addr
                keyMsg = msg
            else:
                self.processMessage( addr, msg )

        if keyMsg != None:
            self.processMessage( keyAddr, keyMsg );

    def processMessage( self, addr, msg ):
        client = self.clients.getClient( self, addr )
        client.touch()
        kind = msg[ 0 ]
        if kind == 'h':
            self.processHello( client )
        elif kind == 'i':
            self.processIRMessage( client, msg )
        else:
            print( '*** unknown message type:', kind )
 
    def processDiscovery( self, addr ):
        self.sendDiscoveryResponse( addr )

    def processHello( self, client ):
        pass

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
                print( '*** failed to process IR message' )
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

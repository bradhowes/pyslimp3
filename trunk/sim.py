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

import asyncore, socket, struct, sys, threading, time
from datetime import datetime, timedelta
import VFD

kServerAddress = ( 'localhost', 3483 )

sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
sock.bind( ( '', 0 ) )
connected = False

keymap = { 'q': 0x0000f702,     # Power
           ',': 0x0000c0f8,     # Volume down
           '.': 0x0000c078,     # Volume up

           's': 0x0000f7c2,     # Stop
           'p': 0x0000f732,     # Play
           'P': 0x0000f7b2,     # Pause

           'f': 0x0000f76e,     # Fast-forward
           'w': 0x0000f70e,     # Rewind

           'u': 0x0000f70b,     # Up
           'l': 0x0000f74b,     # Left
           'd': 0x0000f78b,     # Down
           'r': 0x0000f7cb,     # Right

           'S': 0x0000f72b,     # Shuffle
           'R': 0x0000f7ab,     # Repeat
           'D': 0x0000f703,     # Display
           'M': 0x0000c038,     # Mute
           'H': 0x0000f783,     # MenuHome

           'i': 0x0000f7f6,     # PIP

           '0': 0x0000f776,
           '1': 0x0000f786,
           '2': 0x0000f746,
           '3': 0x0000f7c6,
           '4': 0x0000f726,
           '5': 0x0000f7a6,
           '6': 0x0000f766,
           '7': 0x0000f7e6,
           '8': 0x0000f716,
           '9': 0x0000f796
           }

class KeyReader( asyncore.file_dispatcher ):
    
    def __init__( self, sim ):
        asyncore.file_dispatcher.__init__( self, sys.stdin.fileno() )
        self.sim = sim

    def handle_read( self ):
        data = self.recv( 1024 ).strip()
        if len( data ): self.sim.processKey( data )

    def handle_connect( self ): return
    def handle_write( self ): return
    def readable( self ): return True
    def writable( self ): return False

class ServerSocket( asyncore.dispatcher ):
    
    def __init__( self, sim ):
        asyncore.dispatcher.__init__( self )
        self.sim = sim
        self.create_socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socket.bind( ( '', 0 ) )
        self.set_reuse_addr()
        self.lastScreen = None
        self.foundServer = False

    def emitHeartbeat( self ):
        if self.foundServer:
            self.emitHello()
        else:
            self.emitDiscovery()

    def emitDiscovery( self ):
        rc = self.emit( 'd' + chr( 0 ) * 17 )
        print 'emitDiscovery', self.emit( 'd' + chr( 0 ) * 17 )

    def emitHello( self ):
        print 'emitHello', self.emit( 'h' + chr( 0 ) * 17 )

    def emitKey( self, code ):
        kTicksPerSecond = 625000.0
        timeStamp = time.time()
        format = '>cBIBBI6x'
        for when in ( 0x000112233, 0x00112233 + 0.100 ):
            buffer = struct.pack( format, 'i', 0,
                                  int( when * kTicksPerSecond ) & 0xFFFFFFFF,
                                  0, 0, code )
            self.emit( buffer )

    def emit( self, buffer ):
        return self.socket.sendto( buffer, kServerAddress )

    def handle_connect( self ): 
        pass

    def writable( self ): return False

    def extractLine( self, msg ):
        line = u''
        index = 26

        while ord( msg[ index + 1 ] ) != 0x06:
            index += 18         # Skip over custom data

        index += 4              # Skip over the 'clear and home' commands

        while ord( msg[ index ] ) == VFD.kPrefixCharacter:
            c = msg[ index + 1 ]
            if ord( c ) < 32: c = u'?'
            line += unichr( ord( c ) )
            index += 2

        index += 2
        line += '\n'

        while ord( msg[ index ] ) == VFD.kPrefixCharacter:
            c = msg[ index + 1 ]
            if ord( c ) < 32: c = u'?'
            line += unichr( ord( c ) )
            index += 2

        return line

    def handle_read( self ):
        msg, addr = self.socket.recvfrom( 2048 )
        if msg[ 0 ] == 'D':
            if not self.foundServer:
                self.foundServer = True
                self.emitHello()
        elif msg[ 0 ] == 'l':
            screen = self.extractLine( msg )
            if screen != self.lastScreen:
                print screen.encode('latin-1')
                self.lastScreen = screen

class sim( object ):

    def __init__( self ):
        self.keyReader = KeyReader( self )
        self.serverSocket = ServerSocket( self )

    def run( self ):
        lastHello = datetime.now() + timedelta( 0, -30 )
        while 1:
            now = datetime.now()
            delta = now - lastHello
            if delta.seconds >= 10:
                lastHello = now
                self.serverSocket.emitHeartbeat()
            asyncore.loop( timeout = 10.00, count = 1 )

    def processKey( self, data ):
        key = data[ 0 ]
        code = keymap.get( key )
        if code is not None:
            self.serverSocket.emitKey( code )

if __name__ == "__main__":
    a = sim()
    a.run()

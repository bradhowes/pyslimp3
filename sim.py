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
    
    #
    # VFD characters to Latin-1. Basically, undo the translation found in
    # VFD.py since we want Latin-1 characters to appear on the screen, not the
    # VFD characters.
    #
    kCharacterMap = { 250: 165, # yen sign
                      219: 180, # spacing acute
                      235: 191, # inverted question mark
                      180: 192, # A grave
                      179: 193, # A acute
                      211: 194, # A circumflex
                      178: 195, # A tilde
                      241: 196, # A umlaut
                      209: 197, # A ring
                      206: 198, # AE ligature
                      201: 199, # C cedilla
                      184: 200, # E grave
                      183: 201, # E acute
                      214: 202, # E circumflex
                      247: 203, # E umlaut
                      240: 204, # I grave
                      176: 205, # I acute
                      208: 206, # I circumflex
                      177: 207, # I umlaut
                      203: 208, # ETH
                      222: 209, # N tilde
                      175: 210, # O grave
                      191: 211, # O acute
                      223: 212, # O circumflex
                      207: 213, # O tilde
                      239: 214, # O umlaut
                      120: 215, # multiplication sign
                      189: 216, # O slash
                      182: 217, # U grave
                      181: 218, # U acute
                      244: 219, # U circumflex
                      229: 220, # U umlaut
                      188: 221, # Y acute
                      251: 222, # THORN
                      226: 223, # sharp s
                      164: 224, # a grave
                      163: 225, # a acute
                      195: 226, # a circumflex
                      162: 227, # a tilde
                      225: 228, # a umlaut
                      193: 229, # a ring
                      190: 230, # ae ligature
                      201: 231, # c cedilla
                      168: 232, # e grave
                      167: 233, # e acute
                      198: 234, # e circumflex
                      231: 235, # e umlaut
                      224: 236, # i grave
                      160: 237, # i acute
                      192: 238, # i circumflex
                      161: 239, # i umlaut
                      187: 240, # eth
                      238: 241, # n tilde
                      175: 242, # o grave
                      191: 243, # o acute
                      223: 244, # o circumflex
                      207: 245, # o tilde
                      239: 246, # o umlaut
                      189: 248, # o slash
                      166: 249, # u grave
                      165: 250, # u acute
                      228: 251, # u circumflex
                      245: 252, # u umlaut
                      172: 253, # y acute
                      251: 254, # thorn
                      204: 255, # y umlaut
                      255: 167, # paragraph symbol
                      }

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

    def makeLine( self, msg, start ):
        line = u''
        for index in range( start, start + 80, 2 ):
            c = msg[ index ]
            alt = self.kCharacterMap.get( ord( c ), None )
            if alt:
                c = unichr( alt )
            line += c
        return line

    def handle_read( self ):
        msg, addr = self.socket.recvfrom( 256 )
        if msg[ 0 ] == 'D':
            if not self.foundServer:
                self.foundServer = True
                self.emitHello()
        elif msg[ 0 ] == 'l':
            screen = self.makeLine( msg, 31 )
            screen += '\n'
            screen += self.makeLine( msg, 113 )
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

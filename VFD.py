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

from array import array

def Dots( v ): return int( v, 2 )

#
# Data encoder for the vacuum fluorescent device (VFD) used in the SLIMP3.
# Builds a SLIMP3 'l' (ell) message for the client. The format depicted here
# was gleened from the SLIMP3's VFD.pm file. The prefix characters 0x02 and
# 0x03 found here do not relate to any documentation I have found so far,
# including the Noritake Vacuum Fluorescent Display found on Logitech's code
# repository; I assume they are interpreted and eaten by the SLIMP3 device.
#
# SLIMP3's VFD supports custom character definition; we do not right now.
# However, we do try and map some Latin-1 characters to the equivalent in the
# VFD, such as accents.
#

kLetters = { 'A': ( Dots( '01110' ),
                    Dots( '10001' ),
                    Dots( '11111' ),
                    Dots( '10001' ),
                    Dots( '10001' ) ),
             'C': ( Dots( '01110' ),
                    Dots( '10000' ),
                    Dots( '10000' ),
                    Dots( '10001' ),
                    Dots( '01110' ) ),
             'E': ( Dots( '11111' ),
                    Dots( '10000' ),
                    Dots( '11111' ),
                    Dots( '10000' ),
                    Dots( '11111' ) ),
             'G': ( Dots( '01110' ),
                    Dots( '10000' ),
                    Dots( '10011' ),
                    Dots( '10001' ),
                    Dots( '01110' ) ),
             'I': ( Dots( '01110' ),
                    Dots( '00100' ),
                    Dots( '00100' ),
                    Dots( '00100' ),
                    Dots( '01110' ) ),
             'O': ( Dots( '01110' ),
                    Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '01110' ) ),
             'S': ( Dots( '01110' ),
                    Dots( '10000' ),
                    Dots( '01110' ),
                    Dots( '00001' ),
                    Dots( '11110' ) ),
             'U': ( Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '01110' ) ),
             'Y': ( Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '01010' ),
                    Dots( '00100' ),
                    Dots( '00100' ) ),
             'N': ( Dots( '10001' ),
                    Dots( '11001' ),
                    Dots( '10101' ),
                    Dots( '10011' ),
                    Dots( '10001' ) ),
             'Z': ( Dots( '11111' ),
                    Dots( '00010' ),
                    Dots( '00100' ),
                    Dots( '01000' ),
                    Dots( '11111' ) ),
             'a': ( Dots( '01110' ),
                    Dots( '00001' ),
                    Dots( '01111' ),
                    Dots( '10001' ),
                    Dots( '01111' ) ),
             'c': ( Dots( '01110' ),
                    Dots( '10000' ),
                    Dots( '10000' ),
                    Dots( '10001' ),
                    Dots( '01110' ) ),
             'e': ( Dots( '01110' ),
                    Dots( '10001' ),
                    Dots( '11111' ),
                    Dots( '10000' ),
                    Dots( '01110' ) ),
             'g': ( Dots( '01111' ),
                    Dots( '10001' ),
                    Dots( '01111' ),
                    Dots( '00001' ),
                    Dots( '01110' ) ),
             'i': ( Dots( '01100' ),
                    Dots( '00100' ),
                    Dots( '00100' ),
                    Dots( '00100' ),
                    Dots( '01110' ) ),
             'o': ( Dots( '01110' ),
                    Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '01110' ) ),
             's': ( Dots( '01110' ),
                    Dots( '10000' ),
                    Dots( '01110' ),
                    Dots( '00001' ),
                    Dots( '11110' ) ),
             'u': ( Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '10011' ),
                    Dots( '01100' ) ),
             'y': ( Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '01111' ),
                    Dots( '00001' ),
                    Dots( '01110' ) ),
             'n': ( Dots( '10110' ),
                    Dots( '11001' ),
                    Dots( '10001' ),
                    Dots( '10001' ),
                    Dots( '10001' ) ),
             'z': ( Dots( '11111' ),
                    Dots( '00010' ),
                    Dots( '00100' ),
                    Dots( '01000' ),
                    Dots( '11111' ) ),
             }

kAccents = { '`': ( Dots( '00100' ),
                    Dots( '00010' ) ),
             "'": ( Dots( '00010' ),
                    Dots( '00100' ) ),
             '^': ( Dots( '00100' ),
                    Dots( '01010' ) ),
             'v': ( Dots( '01010' ),
                    Dots( '00100' ) ),
             '.': ( Dots( '00100' ),
                    Dots( '00000' ) ),
             ':': ( Dots( '01010' ),
                    Dots( '00000' ) ),
             '~': ( Dots( '01110' ),
                    Dots( '00000' ) ),
             'C': ( Dots( '00100' ),
                    Dots( '00110' ) ),
             'c': ( Dots( '00100' ),
                    Dots( '01100' ) )
             }

def makeAccentChar( c, a ):
    return tuple( list( kAccents[ a ] ) + list( kLetters[ c ] ) )

def makeCedillaChar( c, a ):
    return tuple( list( kLetters[ c ] ) + list( kAccents[ a ] ) )

class VFD( object ):

    kMinBrightness = 0          # Minimum brightness level for the display
    kMaxBrightness = 3          # Maximum brightness level for the display

    kCustomChars = {}
    for letter in 'AEIOUaeiou':
        for accent in "`'^v.:~":
            kCustomChars[ letter + accent ] = makeAccentChar( letter, accent )

    for letter in 'Nn':
        for accent in "'v~":
            kCustomChars[ letter + accent ] = makeAccentChar( letter, accent )

    for letter in 'CcSs':
        for accent in "'v":
            kCustomChars[ letter + accent ] = makeAccentChar( letter, accent )
            
    for letter in 'Zz':
        for accent in "'.v":
            kCustomChars[ letter + accent ] = makeAccentChar( letter, accent )

    for letter in 'Gg':
        kCustomChars[ letter + accent ] = makeAccentChar( letter, 'v' )

    for letter in 'AaEe':
        kCustomChars[ letter + accent ] = makeCedillaChar( letter, 'C' )

    for letter in 'CcSs':
        kCustomChars[ letter + accent ] = makeCedillaChar( letter, 'c' )

    kCustomChars[ 'O/' ] = ( Dots( '00001' ),
                             Dots( '01110' ),
                             Dots( '10011' ),
                             Dots( '10101' ),
                             Dots( '11001' ),
                             Dots( '01110' ),
                             Dots( '10000' ) )

    kCustomChars[ 'SS' ] = ( Dots( '00000' ),
                             Dots( '01110' ),
                             Dots( '10001' ),
                             Dots( '11110' ),
                             Dots( '10001' ),
                             Dots( '11110' ),
                             Dots( '10000' ) )

    #
    # Latin-1 characters to VFD device character set (non-Japanese version). We
    # are using internal Python Unicode strings, and the first 256 charcters in
    # Unicode match those in latin-1 encodings. So, we offer a translation of
    # Latin-1 characters into matching (or closely matching) VFD characters.
    # Works pretty well.
    #
    kG57128 = { 165: 250, # yen sign
                166: 124, # broken bar
                171: 34,  # left angle quotes
                173: 45,  # soft hyphen
                180: 219, # spacing acute
                187: 34,  # right angle quotes
                191: 235, # inverted question mark
                192: 180, # A grave
                193: 179, # A acute
                194: 211, # A circumflex
                195: 178, # A tilde
                196: 241, # A umlaut
                197: 209, # A ring
                198: 206, # AE ligature
                199: 201, # C cedilla
                200: 184, # E grave
                201: 183, # E acute
                202: 214, # E circumflex
                203: 247, # E umlaut
                204: 240, # I grave
                205: 176, # I acute
                206: 208, # I circumflex
                207: 177, # I umlaut
                208: 203, # ETH
                209: 222, # N tilde
                210: 175, # O grave
                211: 191, # O acute
                212: 223, # O circumflex
                213: 207, # O tilde
                214: 239, # O umlaut
                215: 120, # multiplication sign
                216: 189, # O slash
                217: 182, # U grave
                218: 181, # U acute
                219: 244, # U circumflex
                220: 229, # U umlaut
                221: 188, # Y acute
                222: 251, # THORN
                223: 226, # sharp s
                224: 164, # a grave
                225: 163, # a acute
                226: 195, # a circumflex
                227: 162, # a tilde
                228: 225, # a umlaut
                229: 193, # a ring
                230: 190, # ae ligature
                231: 201, # c cedilla
                232: 168, # e grave
                233: 167, # e acute
                234: 198, # e circumflex
                235: 231, # e umlaut
                236: 224, # i grave
                237: 160, # i acute
                238: 192, # i circumflex
                239: 161, # i umlaut
                240: 187, # eth
                241: 238, # n tilde
                242: 175, # o grave
                243: 191, # o acute
                244: 223, # o circumflex
                245: 207, # o tilde
                246: 239, # o umlaut
                247: 47,  # division sign
                248: 189, # o slash
                249: 166, # u grave
                250: 165, # u acute
                251: 228, # u circumflex
                252: 245, # u umlaut
                253: 172, # y acute
                254: 251, # thorn
                255: 204, # y umlaut

                8216: 39, # left single-quote
                8217: 39, # right single-quote
                8218: 44, # comma
                8219: 39, # reversed right single-quote
                8220: 34, # left double-quote
                8221: 34, # right double-quote
                }

    #
    # Latin-1 characters to VFD device character set (non-Japanese version). We
    # are using internal Python Unicode strings, and the first 256 charcters in
    # Unicode match those in latin-1 encodings. So, we offer a translation of
    # Latin-1 characters into matching (or closely matching) VFD characters.
    # Works pretty well.
    #
    kG57131 = { 166: 0x98, # broken bar
                171: ord('"'),  # left angle quotes
                173: ord('-'),  # soft hyphen
                180: ord("'"), # spacing acute
                187: ord('"'),  # right angle quotes
                191: ord('?'), # inverted question mark
                192: 0x81, # A grave
                193: 0x81, # A acute
                194: 0x82, # A circumflex
                195: 0x82, # A tilde
                196: 0x80, # A umlaut
                197: 0x81, # A ring
                198: 0x90, # AE ligature
                199: 0x99, # C cedilla
                200: ord('E'), # E grave
                201: ord('E'), # E acute
                202: ord('E'), # E circumflex
                203: ord('E'), # E umlaut
                204: ord('I'), # I grave
                205: ord('I'), # I acute
                206: ord('I'), # I circumflex
                207: ord('I'), # I umlaut
                209: ord('N'), # N tilde
                210: ord('O'), # O grave
                211: ord('O'), # O acute
                212: ord('O'), # O circumflex
                213: ord('O'), # O tilde
                214: 0x86, # O umlaut
                215: 0xa5, # multiplication sign
                216: 0x88, # O slash
                217: ord('U'), # U grave
                218: ord('U'), # U acute
                219: ord('U'), # U circumflex
                220: 0x8a, # U umlaut
                221: ord('Y'), # Y acute
                223: 0xe2, # sharp s
                224: 0x84, # a grave
                225: 0x83, # a acute
                226: 0x84, # a circumflex
                227: 0x83, # a tilde
                228: 0xe1, # a umlaut
                229: 0x84, # a ring
                230: 0x91, # ae ligature
                231: 0x99, # c cedilla
                232: ord('e'), # e grave
                233: ord('e'), # e acute
                234: ord('e'), # e circumflex
                235: ord('e'), # e umlaut
                236: ord('i'), # i grave
                237: ord('i'), # i acute
                238: ord('i'), # i circumflex
                239: ord('i'), # i umlaut
                241: 0xee, # n tilde
                242: ord('o'), # o grave
                243: ord('o'), # o acute
                244: ord('o'), # o circumflex
                245: ord('o'), # o tilde
                246: 0xef, # o umlaut
                247: 0xfd,  # division sign
                248: 0x89, # o slash
                249: ord('u'), # u grave
                250: ord('u'), # u acute
                251: ord('u'), # u circumflex
                252: 0xf5, # u umlaut
                253: ord('y'), # y acute
                255: ord('y'), # y umlaut

                8216: ord("'"), # left single-quote
                8217: ord("'"), # right single-quote
                8218: ord(','), # comma
                8219: ord('"'), # reversed right single-quote
                8220: ord('"'), # left double-quote
                8221: ord('"'), # right double-quote
                }

    def __init__( self, brightness ):
        self.brightness = 3
        self.reset()
        self.setBrightness( brightness )

    #
    # Initialize a new array buffer for recording bytes
    #
    def reset( self ):
        kInit = [ ord( 'l' ) ]
        kInit.extend( [ ord( ' ' ) ] * 17 )
        self.buffer = array( 'B', kInit )

    def getBrightness( self ): return self.brightness

    #
    # Set the display's brightness level, clamping the new value between
    # kMinBrightness and kMaxBrightness inclusive . Each display update
    # contains the brightness level.
    #
    def setBrightness( self, value ):
        self.brightness = max( min( value, self.kMaxBrightness ),
                               self.kMinBrightness )
        print 'brightness', self.brightness

    #
    # Apply a delta value to the current brightness setting.
    #
    def changeBrightness( self, delta ):
        self.setBrightness( self.brightness + delta )

    #
    # Add a VFD command to the buffer.
    #
    def _addCommand( self, cmd ):
        self.buffer.extend( ( 0x02, cmd ) ) # Command character prefix

    def translate( self, value ):

        #
        # See if there is a translation to use for the given value.
        #
        alt = self.kG57131.get( value, None )
        if alt is None:
            if value >= 1032 and value <= 1255:
                alt = value - 1000
            elif value > 255 or value < 32:
                alt = 255
        if alt:
            # print '* substituting', alt, 'for', value
            value = alt
        return value

    #
    # Add a display character to the buffer.
    #
    def _addCharacter( self, value ):
        self.buffer.extend( ( 0x03, value ) ) # Display character prefix

    #
    # Make sure a given string of text is exactly 40 characters in length,
    # truncating or adding spaces if necessary.
    #
    def _padLine( self, line ):
        if len( line ) == 40:
            return line
        return line[ 0 : 40 ] + ' ' * ( 40 - len( line ) )

    #
    # Generate a new client message containing display text.
    #
    def build( self, lines, cursor = None ):
        self.reset()

        #
        # Initialize the device, setting its brightness
        #
        self._addCommand( 0x33 )
        self._addCommand( 0x00 )
        self._addCommand( 0x30 )
        self._addCharacter( self.kMaxBrightness - self.brightness )

        #
        # Clear the display
        #
        self._addCommand( 0x06 ) # Entry mode (increment address, cursor)
        self._addCommand( 0x02 ) # Clear and cursor home (first line) 

        #
        # Add the characters of the first line
        #
        for c in self._padLine( lines[ 0 ] ):
            self._addCharacter( self.translate( ord( c ) ) )

        self._addCommand( 0xC0 ) # Move the cursor to the second line

        #
        # Add the characters of the second line
        #
        for c in self._padLine( lines[ 1 ] ):
            self._addCharacter( self.translate( ord( c ) ) )

        #
        # Position and reveal the cursor if asked to.
        #
        if cursor is None or cursor < 0 or cursor > 80:
            self._addCommand( 0x0C ) # Display on, cursor off
        else:

            if cursor < 40:
                
                #
                # Position the cursor on the first line
                #
                self._addCommand( 0x80 + cursor )
            else:
                
                #
                # Position the cursor on the second line
                #
                self._addCommand( 0xC0 + ( cursor - 40 ) )

            self._addCommand( 0x0E ) # Display on, cursor on
            # self._addCommand( 0x0F ) # Display on, cursor on, blink

        return self.buffer.tostring()

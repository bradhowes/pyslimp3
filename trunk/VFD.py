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

kPrefixCommand = 0x02
kPrefixCharacter = 0x03
kStartCustom = 0x40
kMessageHeader = [ ord( 'l' ) ] + [ ord( ' ' ) ] * 17

def Bin( value ): return int( value, 2 )

def Dots( *values ): 
    bits = [ kPrefixCharacter ] * ( len( values ) * 2 )
    index = 1
    for each in values:
        bits[ index ] = Bin( each )
        index += 2
    return tuple( bits )

class IndexGenerator( object ):
    def __init__( self, value ):
        self.next = value
    def __call__( self ):
        value = self.next
        self.next = value + 1
        return value

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

class CustomCharacters( object ):

    kLetters = { 'A': Dots( '01110',
                            '10001',
                            '11111',
                            '10001',
                            '10001' ),
                 'C': Dots( '01110',
                            '10000',
                            '10000',
                            '10001',
                            '01110' ),
                 'E': Dots( '11111',
                            '10000',
                            '11111',
                            '10000',
                            '11111' ),
                 'G': Dots( '01110',
                            '10000',
                            '10011',
                            '10001',
                            '01110' ),
                 'I': Dots( '01110',
                            '00100',
                            '00100',
                            '00100',
                            '01110' ),
                 'N': Dots( '10001',
                            '11001',
                            '10101',
                            '10011',
                            '10001' ),
                 'O': Dots( '01110',
                            '10001',
                            '10001',
                            '10001',
                            '01110' ),
                 'S': Dots( '01110',
                            '10000',
                            '01110',
                            '00001',
                            '11110' ),
                 'U': Dots( '10001',
                            '10001',
                            '10001',
                            '10001',
                            '01110' ),
                 'Y': Dots( '10001',
                            '10001',
                            '01010',
                            '00100',
                            '00100' ),
                 'Z': Dots( '11111',
                            '00010',
                            '00100',
                            '01000',
                            '11111' ),
                 'a': Dots( '01110',
                            '00001',
                            '01111',
                            '10001',
                            '01111' ),
                 'e': Dots( '01110',
                            '10001',
                            '11111',
                            '10000',
                            '01110' ),
                 'g': Dots( '01111',
                            '10001',
                            '01111',
                            '00001',
                            '01110' ),
                 'i': Dots( '01100',
                            '00100',
                            '00100',
                            '00100',
                            '01110' ),
                 'n': Dots( '10110',
                            '11001',
                            '10001',
                            '10001',
                            '10001' ),
                 'u': Dots( '10001',
                            '10001',
                            '10001',
                            '10011',
                            '01100' ),
                 'y': Dots( '10001',
                            '10001',
                            '01111',
                            '00001',
                            '01110' ),
                 }

    #
    # Some letters use the same defintion for both cases.
    #
    for letter in 'COSZ':
        kLetters[ letter.lower() ] = kLetters[ letter ]

    #
    # Definitions for diacritical marks
    #
    kAccents = { '`': Dots( '00100', # agrave
                            '00010' ),
                 "'": Dots( '00010', # acute
                            '00100' ),
                 '^': Dots( '00100', # circumflex
                            '01010' ),
                 'v': Dots( '01010', # invered circumflex
                            '00100' ),
                 '.': Dots( '00100', # dot
                            '00000' ),
                 ':': Dots( '01010', # umlaut
                            '00000' ),
                 '~': Dots( '01110', # tilde
                            '00000' ),
                 'C': Dots( '00100', # reverse cedilla
                            '00110' ),
                 'c': Dots( '00100', # cedilla
                            '01100' )
                 }

    indices = IndexGenerator( 1000 )
    kVolumeBar0 = indices()     # Empty volume block
    kVolumeBar1 = indices()
    kVolumeBar2 = indices()
    kVolumeBar3 = indices()
    kVolumeBar4 = indices()
    kVolumeBar5 = indices()
    kVolumeBarBegin = indices()
    kVolumeBarEnd = indices()

    kRatingEmpty = indices()
    kRatingFilled = indices()
    kRatingHalf = indices()

    kCharacterMap = { 0x7E: Dots( '00000', # tilde
                                  '00000',
                                  '01000',
                                  '10101',
                                  '00010',
                                  '00000',
                                  '00000' ),

                      0x82: ord( ',' ),
                      0x83: ord( 'f' ),
                      0x84: ord( '"' ),

                      0x85: Dots( '00000', # ...
                                  '00000',
                                  '00000',
                                  '00000',
                                  '00000',
                                  '00000',
                                  '10101' ),

                      0x8A: kAccents[ 'v' ] + kLetters[ 'S' ], # S v
                      0x8E: kAccents[ 'v' ] + kLetters[ 'Z' ], # Z v

                      0x91: ord( "'" ),
                      0x92: ord( "'" ),
                      0x93: ord( '"' ),
                      0x94: ord( '"' ),

                      0x95: Dots( '00000', # filled circle
                                  '00100',
                                  '01110',
                                  '01110',
                                  '00100',
                                  '00000',
                                  '00000' ),

                      0x96: ord( '-' ),
                      0x97: ord( '-' ),

                      0x98: Dots( '01000', # raised tilde
                                  '10101',
                                  '00010',
                                  '00000',
                                  '00000',
                                  '00000',
                                  '00000' ),

                      0x9A: kAccents[ 'v' ] + kLetters[ 's' ], # s v
                      0x9E: kAccents[ 'v' ] + kLetters[ 'z' ], # z v

                      0x9F: kAccents[ ':' ] + kLetters[ 'Y' ], # Y umlaut

                      0xC0: kAccents[ '`' ] + kLetters[ 'A' ], # A grave
                      0xC1: kAccents[ "'" ] + kLetters[ 'A' ], # A acute
                      0xC2: kAccents[ '^' ] + kLetters[ 'A' ], # A circumflex
                      0xC3: kAccents[ '~' ] + kLetters[ 'A' ], # A tilde
                      0xC4: kAccents[ ':' ] + kLetters[ 'A' ], # A umlaut
                      0xC5: kAccents[ '.' ] + kLetters[ 'A' ], # A ring

                      0xC6: Dots( '00111', # AE ligature
                                  '01100',
                                  '10100',
                                  '10111',
                                  '11100',
                                  '10100',
                                  '10111' ),

                      0xC7: kLetters[ 'C' ] + kAccents[ 'c' ], # C cedilla

                      0xC8: kAccents[ '`' ] + kLetters[ 'E' ], # E grave
                      0xC9: kAccents[ "'" ] + kLetters[ 'E' ], # E acute
                      0xCA: kAccents[ '^' ] + kLetters[ 'E' ], # E circumflex
                      0xCB: kAccents[ ':' ] + kLetters[ 'E' ], # E umlaut

                      0xCC: kAccents[ '`' ] + kLetters[ 'I' ], # I grave
                      0xCD: kAccents[ "'" ] + kLetters[ 'I' ], # I acute
                      0xCE: kAccents[ '^' ] + kLetters[ 'I' ], # I circumflex
                      0xCF: kAccents[ ':' ] + kLetters[ 'I' ], # I umlaut

                      0xD0: Dots( '11100', # Eth
                                  '10010',
                                  '10001',
                                  '11001',
                                  '10001',
                                  '10010',
                                  '11100' ),

                      0xD1: kAccents[ '~' ] + kLetters[ 'N' ], # N tilde

                      0xD2: kAccents[ '`' ] + kLetters[ 'O' ], # O grave
                      0xD3: kAccents[ "'" ] + kLetters[ 'O' ], # O acute
                      0xD4: kAccents[ '^' ] + kLetters[ 'O' ], # O circumflex
                      0xD5: kAccents[ '~' ] + kLetters[ 'O' ], # O tilde
                      0xD6: kAccents[ ':' ] + kLetters[ 'O' ], # O umlaut
                      0xD7: Dots( '00000', # multiplication symbol
                                  '00000',
                                  '01010',
                                  '00100',
                                  '01010',
                                  '00000',
                                  '00000' ),
                                  
                      0xD8: Dots( '00001', # O slash
                                  '01110',
                                  '10011',
                                  '10101',
                                  '11001',
                                  '01110',
                                  '10000' ),

                      0xD9: kAccents[ '`' ] + kLetters[ 'U' ], # U grave
                      0xDA: kAccents[ "'" ] + kLetters[ 'U' ], # U acute
                      0xDB: kAccents[ '^' ] + kLetters[ 'U' ], # U circumflex
                      0xDC: kAccents[ ':' ] + kLetters[ 'U' ], # U umlaut

                      0xDD: kAccents[ "'" ] + kLetters[ 'Y' ], # Y acute

                      0xDF: Dots( '00000', # sharp s
                                  '01110',
                                  '10001',
                                  '11110',
                                  '10001',
                                  '11110',
                                  '10000' ),

                      0xE0: kAccents[ '`' ] + kLetters[ 'a' ], # a grave
                      0xE1: kAccents[ "'" ] + kLetters[ 'a' ], # a acute
                      0xE2: kAccents[ '^' ] + kLetters[ 'a' ], # a circumflex
                      0xE3: kAccents[ '~' ] + kLetters[ 'a' ], # a tilde
                      0xE4: kAccents[ ':' ] + kLetters[ 'a' ], # a umlaut
                      0xE5: kAccents[ '.' ] + kLetters[ 'a' ], # a ring

                      0xE6: Dots( '00000', # ae ligature
                                  '00000',
                                  '11010',
                                  '00101',
                                  '11111',
                                  '10100',
                                  '11111' ),

                      0xE7: kLetters[ 'c' ] + kAccents[ 'c' ], # c cedilla

                      0xE8: kAccents[ '`' ] + kLetters[ 'e' ], # E grave
                      0xE9: kAccents[ "'" ] + kLetters[ 'e' ], # E acute
                      0xEA: kAccents[ '^' ] + kLetters[ 'e' ], # E circumflex
                      0xEB: kAccents[ ':' ] + kLetters[ 'e' ], # E umlaut

                      0xEC: kAccents[ '`' ] + kLetters[ 'i' ], # I grave
                      0xED: kAccents[ "'" ] + kLetters[ 'i' ], # I acute
                      0xEE: kAccents[ '^' ] + kLetters[ 'i' ], # I circumflex
                      0xEF: kAccents[ ':' ] + kLetters[ 'i' ], # I umlaut
                      
                      0xF0: Dots( '01100', # eth
                                  '00010',
                                  '01111',
                                  '10001',
                                  '10001',
                                  '10001',
                                  '01110' ),

                      0xF1: kAccents[ '~' ] + kLetters[ 'n' ], # n tilde

                      0xF2: kAccents[ '`' ] + kLetters[ 'o' ], # o grave
                      0xF3: kAccents[ "'" ] + kLetters[ 'o' ], # o acute
                      0xF4: kAccents[ '^' ] + kLetters[ 'o' ], # o circumflex
                      0xF5: kAccents[ '~' ] + kLetters[ 'o' ], # o tilde
                      0xF6: kAccents[ ':' ] + kLetters[ 'o' ], # o umlaut

                      0xF7: Dots( '00000', # division symbol
                                  '00000',
                                  '00100',
                                  '11111',
                                  '00100',
                                  '00000',
                                  '00000' ),

                      0xF8: Dots( '00001', # o slash
                                  '01110',
                                  '10011',
                                  '10101',
                                  '11001',
                                  '01110',
                                  '10000' ),

                      0xF9: kAccents[ '`' ] + kLetters[ 'u' ], # u grave
                      0xFA: kAccents[ "'" ] + kLetters[ 'u' ], # u acute
                      0xFB: kAccents[ '^' ] + kLetters[ 'u' ], # u circumflex
                      0xFC: kAccents[ ':' ] + kLetters[ 'u' ], # u umlaut

                      0xFD: kAccents[ "'" ] + kLetters[ 'y' ], # y acute
                      0xFF: kAccents[ ':' ] + kLetters[ 'y' ], # y umlaut

                      #
                      # Volume bar characters
                      #
                      kVolumeBar1: Dots( '11111',
                                         '00000',
                                         '10000',
                                         '10000',
                                         '10000',
                                         '00000',
                                         '11111' ),
                      kVolumeBar2: Dots( '11111',
                                         '00000',
                                         '11000',
                                         '11000',
                                         '11000',
                                         '00000',
                                         '11111' ),
                      kVolumeBar3: Dots( '11111',
                                         '00000',
                                         '11100',
                                         '11100',
                                         '11100',
                                         '00000',
                                         '11111' ),
                      kVolumeBar4: Dots( '11111',
                                         '00000',
                                         '11110',
                                         '11110',
                                         '11110',
                                         '00000',
                                         '11111' ),
                      kVolumeBar5: Dots( '11111',
                                         '00000',
                                         '11111',
                                         '11111',
                                         '11111',
                                         '00000',
                                         '11111' ),
                      kVolumeBar0: Dots( '11111',
                                         '00000',
                                         '00000',
                                         '00000',
                                         '00000',
                                         '00000',
                                         '11111' ),
                      kVolumeBarBegin: Dots( '00000',
                                             '00001',
                                             '00011',
                                             '00011',
                                             '00011',
                                             '00001',
                                             '00000' ),
                      kVolumeBarEnd: Dots( '00000',
                                           '10000',
                                           '11000',
                                           '11000',
                                           '11000',
                                           '10000',
                                           '00000' ),
                      kRatingEmpty: Dots( '01010',
                                          '10101',
                                          '10001',
                                          '10001',
                                          '10001',
                                          '01010',
                                          '00100', ),
                      kRatingHalf: Dots( '01010',
                                         '10001',
                                         '10001',
                                         '11111',
                                         '11111',
                                         '01110',
                                         '00100', ),
                      kRatingFilled: Dots( '01010',
                                           '11111', 
                                           '11111',
                                           '11111',
                                           '11111',
                                           '01110',
                                           '00100', ),
                      }

    def __init__( self ):
        self.lookup = {}
        self.inuse = []

    def translate( self, value ):
        alt = self.kCharacterMap.get( value )
        if alt is None:
            return value
        if type( alt ) is type( 0 ):
            # print '* ', hex( value ), alt
            return alt
        index = self.lookup.get( value )
        if index is None:
            index = len( self.inuse )
            self.inuse.append( alt )
            self.lookup[ value ] = index
        # print '* ', hex( value ), index
        return index

    def addMaps( self, buffer ):
        index = 0
        for each in self.inuse:
            buffer.extend( ( kPrefixCommand, kStartCustom + index * 8 ) )
            buffer.extend( each )
            if len( each ) == 7:
                buffer.extend( ( kPrefixCharacter, 0 ) ) # 'underline' line
            index += 1

class Buffer( object ):
    
    def __init__( self, initializer = '' ):
        from array import array
        self.buffer = array( 'B', initializer )

    def addCommand( self, cmd, value = None ):
        if value is None:
            self.buffer.extend( ( kPrefixCommand, cmd ) )
        else:
            self.buffer.extend( ( kPrefixCommand, cmd, kPrefixCharacter,
                                  value ) )

    def addCharacter( self, value ):
        self.buffer.extend( ( kPrefixCharacter, value ) )

    def extend( self, value ):
        if isinstance( value, Buffer ):
            self.buffer.extend( value.buffer )
        else:
            self.buffer.extend( value )

    def getData( self ): return self.buffer.tostring()

    def __len__( self ): return len( self.buffer )

class VFD( object ):

    kMinBrightness = 0          # Minimum brightness level for the display
    kMaxBrightness = 4          # Maximum brightness level for the display

    def __init__( self, brightness ):
        self.brightness = self.kMaxBrightness
        self.setBrightness( brightness )

    #
    # Initialize a new array buffer for recording bytes
    #
    def makeBuffers( self ):
        self.customCharacters = CustomCharacters()
        return Buffer( kMessageHeader ), Buffer()

    def getBrightness( self ): 
        return self.brightness

    #
    # Set the display's brightness level, clamping the new value between
    # kMinBrightness and kMaxBrightness inclusive . Each display update
    # contains the brightness level.
    #
    def setBrightness( self, value ):
        self.brightness = max( min( value, self.kMaxBrightness ),
                               self.kMinBrightness )
        print( value, self.brightness )

    #
    # Apply a delta value to the current brightness setting.
    #
    def changeBrightness( self, delta ):
        self.setBrightness( self.brightness + delta )

    def translate( self, value ):

        #
        # See if there is a translation to use for the given value.
        #
        value = self.customCharacters.translate( value )
        if value > 1000 and value < 1255:
            value -= 1000
        if value > 255:
            value = 255
        return value

    #
    # Make sure a given string of text is exactly 40 characters in length,
    # truncating or adding spaces if necessary.
    #
    def padLine( self, line ):
        if len( line ) == 40:
            return line
        return line[ 0 : 40 ] + ' ' * ( 40 - len( line ) )

    #
    # Generate a new client message containing display text.
    #
    def build( self, lines, cursor = None ):

        buffer, text = self.makeBuffers()

        #
        # DEBUG: buffer starts out with 18 characters in it
        #
        # print len( buffer )

        #
        # Initialize the device, setting its brightness and clearing the
        # display
        #
        buffer.addCommand( 0x33 )
        buffer.addCommand( 0x00 )

        if self.brightness:
            buffer.addCommand( 0x30, self.kMaxBrightness - self.brightness )
        else:
            buffer.addCommand( 0x30, 0 )

        # print 'len( buffer )', len( buffer )

        #
        # Translate the characters of the first line.
        #
        for c in self.padLine( lines[ 0 ] ):
            if self.brightness:
                text.addCharacter( self.translate( ord( c ) ) )
            else:
                text.addCharacter( ord( ' ' ) )

        #
        # Move the cursor to the second line.
        #
        text.addCommand( 0xC0 )

        #
        # Translate the characters of the second line.
        #
        for c in self.padLine( lines[ 1 ] ):
            if self.brightness:
                text.addCharacter( self.translate( ord( c ) ) )
            else:
                text.addCharacter( ord( ' ' ) )

        #
        # Done processing the text data. Add any custom character maps to the
        # buffer before we add the translated display data.
        #
        self.customCharacters.addMaps( buffer )
        
        #
        # DEBUG: buffer now has 26 + 18 * N characters in it, where N is
        # the number of custom characters added by our CustomCharacter object
        #
        # print 'len( buffer )', len( buffer )

        #
        # Clear the display
        #
        buffer.addCommand( 0x06 ) # Entry mode (increment address, cursor)
        buffer.addCommand( 0x02 ) # Clear and cursor home (first line) 

        #
        # Add the characters to display.
        #
        buffer.extend( text )

        #
        # Position and reveal the cursor if asked to.
        #
        if cursor is None or cursor < 0 or cursor > 80:
            buffer.addCommand( 0x0C ) # Display on, cursor off
        else:

            if cursor < 40:
                
                #
                # Position the cursor on the first line
                #
                buffer.addCommand( 0x80 + cursor )
            else:
                
                #
                # Position the cursor on the second line
                #
                buffer.addCommand( 0xC0 + ( cursor - 40 ) )

            buffer.addCommand( 0x0E ) # Display on, cursor on

        return buffer.getData()

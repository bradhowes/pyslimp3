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

#
# Data encoder for the vacuum fluorescent device (VFD) used in the SLIMP3.
# Builds a SLIMP3 'l' (ell) message for the client. The format depicted here
# was gleened from the SLIMP3's VFD.pm file. The prefix characters 0x02 and
# 0x03 found here do not relate to any documentation I have found so far,
# including the Noritake Vacuum Fluorescent Display found on Logitech's code
# repository; I assume they are interpreted and eaten by the SLIMP3 device.
#
# SLIMP3's VFD supports custom character definition; we do not.
#
class VFD( object ):

    kMinBrightness = 0          # Minimum brightness level for the display
    kMaxBrightness = 3          # Maximum brightness level for the display

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

    #
    # Add a display character to the buffer.
    #
    def _addCharacter( self, value ):
        if value > 0xFF:
            value = 0xFF
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
    def build( self, lines, cursor ):
        self.reset()
        
        #
        # Initialize the device, setting its brightness
        #
        self._addCommand( 0x33 ) # Function set command (?)
        self._addCommand( 0x00 ) # Brightness (full)
        self._addCommand( 0x30 ) # Function set command
        self._addCharacter( self.kMaxBrightness - self.brightness )

        #
        # Clear the display
        #
        self._addCommand( 0x06 ) # Entry mode (increment address, cursor)
        self._addCommand( 0x03 ) # Clear and cursor home (first line) 

        #
        # Add the characters of the first line
        #
        for c in self._padLine( lines[ 0 ] ):
            self._addCharacter( ord( c ) )

        self._addCommand( 0xC0 ) # Move the cursor to the second line

        #
        # Add the characters of the second line
        #
        for c in self._padLine( lines[ 1 ] ):
            self._addCharacter( ord( c ) )

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

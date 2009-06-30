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
from random import randrange
from Content import *
from KeyProcessor import *

#
# Align text in center of line 
#
def centerAlign( value ):
    size = len( value )
    if size >= kDisplayWidth: return value
    return ' ' * ( ( kDisplayWidth - size ) / 2 ) + value

#
# Align text to the right
#
def rightAlign( value ):
    size = len( value )
    if size >= kDisplayWidth: return value
    return ' ' * ( ( kDisplayWidth - size ) ) + value

#
# Format a quantity with units, supplying the proper version of the units tag
# depending on the value to format (sinular vs. plural)
#
def formatQuantity( value, singular, plural = None, format = '%d %s' ):
    if plural is None: plural = singular + 's'
    if value == 1: kind = singular
    else: kind = plural
    return format % ( value, kind )

#
# Format a seconds value into MM:SS or HH::MM:SS formatted string
#
def getHHMMSS( secs ):
    if secs < 60:
        return '0:%02d' % secs
    elif secs < 3600:
        
        #
        # Non-zero minutes component
        #
        mins = secs / 60
        secs -= mins * 60
        return '%d:%02d' % ( mins, secs )
    else:
        
        #
        # Non-zero hours component
        #
        hrs = secs / 3600
        secs -= hrs * 3600
        mins = secs / 60
        secs -= mins * 60
        return '%d:%02d:%02d' % ( hrs, mins, secs )

#
# Base class of all display generators. Derived classes must override
# generate() with a method that creates and returns a Content instance.
#
class DisplayGenerator( object ):

    def __init__( self ):
        self.keyMap = {}
        self.fillKeyMap()

    #
    # Determine if this display generator is a temporary overlay. Derived
    # classes should override if they act as an overlay.
    #
    def isOverlay( self ): return False

    #
    # Install handlers for digit keyCode values.
    #
    def fillKeyMap( self ):
        for digit in range( 10 ):
            key = str( digit )
            proc = getattr( self, 'digit' + key )
            self.addKeyMapEntry( key, kModFirst, proc )

    #
    # Add an entry to the display generator's keymap. Note that there is no
    # check for conflicts.
    #
    def addKeyMapEntry( self, key, mods, proc ):
        keyMap = self.keyMap
        for keyCode in makeKeyCodes( key, mods ):
            keyMap[ keyCode ] = proc

    #
    # Look for a keyMap registration for the given keyCode. If found, execute
    # the found procedure, and return the new screen generator to install.
    # Otherwise, return None to signal that the keyCode was not handled.
    #
    def processKeyCode( self, keyCode ):
        proc = self.keyMap.get( keyCode )
        if proc: 
            return proc()
        return None

    #
    # Generate display content. Derived classes must implement and return a
    # Content object containing the display data.
    #
    def generate( self ):
        raise NotImplementedError, 'DisplayGenerator.generate'

    # 
    # Derived classes must override digit() (or the specific digit#() methods)
    # to handle digit key events.
    #
    def digit( self, digit ): return None
    def digit0( self ): return self.digit( 0 )
    def digit1( self ): return self.digit( 1 )
    def digit2( self ): return self.digit( 2 )
    def digit3( self ): return self.digit( 3 )
    def digit4( self ): return self.digit( 4 )
    def digit5( self ): return self.digit( 5 )
    def digit6( self ): return self.digit( 6 )
    def digit7( self ): return self.digit( 7 )
    def digit8( self ): return self.digit( 8 )
    def digit9( self ): return self.digit( 9 )

#
# Generate a 'powered off' display like the original SLIMP3.
#
class ClockGenerator( DisplayGenerator ):
    
    def __init__( self ):
        DisplayGenerator.__init__( self )
        self.timestamp = datetime.now()
        self.offset = 0
        self.width = 0

    #
    # Generate display content
    #
    def generate( self ):
        now = datetime.now()
        line1 = now.strftime( '%A %B %d, %Y' )
        line2 = now.strftime( '%X' )
        width = max( len( line1 ), len( line2 ) )
        delta = now - self.timestamp
        if delta.seconds > 8 or width != self.width:
            self.timestamp = now
            self.width = width
            self.offset = randrange( kDisplayWidth - width )
        offset = self.offset
        line1 = ' ' * ( offset + ( width - len( line1 ) ) / 2 ) + line1
        line2 = ' ' * ( offset + ( width - len( line2 ) ) / 2 ) + line2
        return Content( [ line1, line2 ] )

class BlankScreen( DisplayGenerator ):

    kEmptyContent = Content( [ '', '' ] )

    #
    # Generate display content
    #
    def generate( self ):
        return self.kEmptyContent

#
# Base class for all display generators that utilize iTunes as a data source.
#
class iTunesSourceGenerator( DisplayGenerator ):
    def __init__( self, source ):
        DisplayGenerator.__init__( self )
        self.source = source

#
# Volume display generator. Shows the current volume setting as a line of
# filled blocks.
#
class VolumeGenerator( iTunesSourceGenerator ):

    def __init__( self, source ):
        iTunesSourceGenerator.__init__( self, source )

    #
    # Generate display content.
    #
    def generate( self ):
        volume = self.source.getVolume()
        line2 = '%3d ' % ( volume, )
        line2 += chr( 255 ) * ( volume * ( kDisplayWidth - 4 ) / 100 )
        return Content( [ centerAlign( 'Volume' ), line2 ] )

    #
    # Override of DisplayGenerator method. Translate digit values 0-9 into
    # iTunes volume values 0-100
    #
    def digit( self, digit ):
        self.source.setVolume( int( digit * 100.0 / 9.0 + 0.5 ) )
        return self

#
# Base class for display generators that show various iTunes state values.
#
class StateGenerator( iTunesSourceGenerator ):

    #
    # Convert boolean values to text tags
    #
    def getBoolTag( self, state ):
        if state: return 'ON'
        return 'OFF'

    #
    # Generate a new Content instance to render the given state information.
    #
    def makeContent( self, name, state ):
        return Content( [ centerAlign( '* %s %s *' % ( name, state ) ) ] )

    #
    # Generate a new Content instance to render the given boolean state
    #
    def makeBoolContent( self, name, state ):
        return self.makeContent( name, self.getBoolTag( state ) )

#
# Mute state display generator.
#
class MuteStateGenerator( StateGenerator ):
    def generate( self ):
        return self.makeBoolContent( 'Mute', self.source.getMute() )

#
# Shuffle mode state display generator.
#
class ShuffleStateGenerator( StateGenerator ):
    def generate( self ):
        return self.makeBoolContent( 'Shuffling', self.source.getShuffle() )

#
# Repeat mode state display generator.
#
class RepeatStateGenerator( StateGenerator ):
    kTagMapping = { 'k.all': 'ALL', 'k.one': 'SONG', 'k.off': 'OFF' }
    def generate( self ):
        return self.makeContent( 
            'Repeat', self.kTagMapping[ repr( self.source.getRepeat() ) ] )

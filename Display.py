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
from VFD import CustomCharacters

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
        return u'0:%02d' % secs

    elif secs < 3600:

        #
        # Non-zero minutes component
        #
        mins = int( secs / 60 )
        secs -= mins * 60
        return u'%d:%02d' % ( mins, secs )

    else:

        #
        # Non-zero hours component
        #
        hrs = int( secs / 3600 )
        secs -= hrs * 3600
        mins = int( secs / 60 )
        secs -= mins * 60
        return u'%d:%02d:%02d' % ( hrs, mins, secs )

#
# Base class of all display generators. Derived classes must override
# generate() with a method that creates and returns a Content instance.
#
class DisplayGenerator( object ):

    def __init__( self, client, prevLevel = None ):
        self.client = client
        self.prevLevel = prevLevel
        self.source = client.getSource()
        self.keyMap = {}
        self.fillKeyMap()

    def getClient( self ): return self.client

    def getSource( self ): return self.source

    #
    # Determine if this display generator is a temporary overlay. Derived
    # classes should override if they act as an overlay.
    #
    def isOverlay( self ): return False

    #
    # Install handlers for digit keyCode values.
    #
    def fillKeyMap( self ):
        self.addKeyMapEntry( kArrowLeft, ( kModFirst, ), self.left )
        for digit in range( 10 ):
            key = str( digit )
            proc = getattr( self, 'digit' + key )
            self.addKeyMapEntry( key, ( kModFirst, ), proc )

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
    # Move to a previous display level if given in the constructor. Otherwise,
    # just return self.
    #
    def left( self ):
        if self.prevLevel:
            return self.prevLevel
        return self

    # 
    # Derived classes may override digit() (or the specific digit#() methods)
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
# Generate a 'powered off' display like the original SliMP3.
#
class ClockGenerator( DisplayGenerator ):

    def __init__( self, client ):
        DisplayGenerator.__init__( self, client )
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
        
        #
        # Move the time every 8 seconds or so.
        #
        if delta.seconds > 8 or width != self.width:
            self.timestamp = now
            self.width = width
            self.offset = randrange( kDisplayWidth - width )
        offset = self.offset
        line1 = ' ' * ( offset + ( width - len( line1 ) ) / 2 ) + line1
        line2 = ' ' * ( offset + ( width - len( line2 ) ) / 2 ) + line2
        return Content( [ line1, line2 ] )

#
# Generate a blank screen.
#
class BlankScreen( DisplayGenerator ):

    kEmptyContent = Content( [ '', '' ] )

    #
    # Generate display content
    #
    def generate( self ):
        return self.kEmptyContent

#
# Obtain a Unicode string containing characters that show a 'progress'
# indicator for a given value using a given number of characters. The width
# parameter is the number of characters used for the indicator; the total size
# will be width + 2 due to the start and end indicator caps. The value
# parameter must be a floating-point value from 0.0 - 1.0.
#
def generateProgressIndicator( width, value ):

    #
    # Restrict to range [0.0,1.0]
    #
    value = max( min( value, 1.0 ), 0.0 )

    #
    # Calculate the number of 'on' bars for the given value.
    #
    numBars = int( width * 5 * value )

    #
    # There are 5 vertical bars in one character position. Calculate the number
    # of these full characters
    #
    fullBars = numBars / 5
    
    #
    # Calculate the number of position with no bars lit
    #
    emptyBars = width - fullBars
    
    #
    # Calculate the number of bars lit in the last character of the indicator.
    #
    lastBar = numBars % 5
    
    #
    # Build the indicator.
    #
    indicator = unichr( CustomCharacters.kVolumeBarBegin )
    if fullBars > 0:
        indicator += unichr( CustomCharacters.kVolumeBar5 ) * fullBars
    if lastBar > 0:
        indicator += unichr( CustomCharacters.kVolumeBar0 + lastBar )
        emptyBars -= 1
    if emptyBars > 0:
        indicator += unichr( CustomCharacters.kVolumeBar0 ) * emptyBars
    indicator += unichr( CustomCharacters.kVolumeBarEnd )

    return indicator

#
# Volume display generator. Shows the current volume setting as a line of
# filled blocks.
#
class VolumeGenerator( DisplayGenerator ):

    #
    # Generate display content.
    #
    def generate( self ):
        volume = self.source.getVolume()
        line2 = u'%3d' % ( volume, )

        #
        # Generate a progress indicator using 20 characters to show current
        # volume (scaled from [0-100] to [0.0-1.0])
        #
        line2 += generateProgressIndicator( 20, volume / 100.0 )
        return Content( [ centerAlign( 'Volume' ), centerAlign( line2 ) ] )

    #
    # Override of DisplayGenerator method. Translate digit values 0-9 into
    # iTunes volume values 0-100
    #
    def digit( self, digit ):
        if digit == 0:
            digit = 10
        self.source.setVolume( digit * 10 )
        return self

#
# Base class for display generators that show various iTunes state values.
#
class StateGenerator( DisplayGenerator ):

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
    
    #
    # Mapping of iTunes repeat states to strings
    #
    kTagMapping = { 'k.all': 'ALL', 'k.one': 'SONG', 'k.off': 'OFF' }

    def generate( self ):
        return self.makeContent( 
            'Repeat', self.kTagMapping[ repr( self.source.getRepeat() ) ] )

#
# Base class for all overlay (temporary) displays
#
class OverlayDisplay( DisplayGenerator ):
    
    #
    # Determine if this display generator is a temporary overlay.
    #
    def isOverlay( self ): return True

#
# General notification display that temporarily shows one or two lines of text,
# centered on the display.
#
class NotificationDisplay( OverlayDisplay ):

    def __init__( self, client, prevLevel, line1, line2 = '' ):
        OverlayDisplay.__init__( self, client, prevLevel )
        self.line1 = centerAlign( line1 )
        self.line2 = centerAlign( line2 )

    def generate( self ):
        return Content( [ self.line1, self.line2 ] )

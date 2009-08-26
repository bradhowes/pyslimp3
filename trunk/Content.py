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

from VFD import *

kDisplayHeight = 2              # Number of lines in display
kDisplayWidth = 40              # Number of characters in line
kDisplayHeightRange = range( kDisplayHeight )
kBlankOverlays = [ '' ] * kDisplayHeight

#
# Representation of display content. Each display generator outputs an instance
# of this class. An Animator will invoke the render() method to generate actual
# text output.
#
class Content:

    #
    # List of characters that do not require a space before them at the start
    # of an overlay string
    #
    kNoSpacePrefix = ( u' ',
                       unichr( CustomCharacters.kVolumeBarBegin ),
                       )

    #
    # Constructor. The 'lines' value must be a list, as must be 'overlays' if
    # it is given.
    #
    def __init__( self, lines, rightOverlays = kBlankOverlays ):

        #
        # Normalize content so that we have kDisplayHeight lines
        #
        if len( lines ) < kDisplayHeight:
            lines.extend( [ '' ] * ( kDisplayHeight - len( lines ) ) )
        self.lines = lines

        if rightOverlays is None:
            rightOverlays = kBlankOverlays
        elif id( rightOverlays ) is not id( kBlankOverlays ):

            count = len( rightOverlays )
            for index in range( count ):
                rightOverlay = rightOverlays[ index ]
                
                #
                # Add a space if the overlay has text, and the first character
                # is not in the kNoSpacePrefix list.
                #
                if len( rightOverlay ) and \
                        rightOverlay[ 0 ] not in self.kNoSpacePrefix:
                    rightOverlays[ index ] = u' ' + rightOverlay

            #
            # Normalize overlays so that we have kDisplayHeight of them
            #
            if count < kDisplayHeight:
                rightOverlays.extend( [ '' ] * ( kDisplayHeight - count ) )

        self.rightOverlays = rightOverlays

        #
        # Calculate how much to scroll to see the end of the line.
        #
        self.shiftsNeeded = []
        for index in kDisplayHeightRange:
            remaining = kDisplayWidth
            line = lines[ index ]
            rightOverlay = rightOverlays[ index ]
            remaining -= len( rightOverlay )
            shiftNeeded = max( len( line ) - remaining, 0 )
            self.shiftsNeeded.append( shiftNeeded )

    def getShiftsNeeded( self ): return self.shiftsNeeded

    def getLine( self, index ): return self.lines[ index ]

    def getRightOverlay( self, index ): return self.rightOverlays[ index ]

    #
    # Generate an text block from the content. Returns the rendered text block.
    #
    def render( self, offsets = None ):
        output = [ None ] * kDisplayHeight
        for index in kDisplayHeightRange:
            line = self.lines[ index ]

            #
            # Truncate the left part of the line if desired to cause a
            # scrolling effect to show long lines.
            #
            if offsets and offsets[ index ] > 0:
                line = line[ offsets[ index ] : ]

            #
            # Force the line to be kDisplayWidth characters wide, either by
            # padding or truncation.
            #
            size = len( line )
            if size < kDisplayWidth: 
                line += ' ' * ( kDisplayWidth - size )
            elif size > kDisplayWidth:
                line = line[ : kDisplayWidth ]

            #
            # Apply overlay text if it exists
            #
            rightOverlay = self.rightOverlays[ index ]
            if len( rightOverlay ) > 0:
                size = len( rightOverlay )
                line = line[ : kDisplayWidth - size ] + rightOverlay
            output[ index ] = line
        return output

    #
    # Determine if this Content instance has different content lines than
    # another one.
    #
    def hasDifferentLines( self, rhs ):
        for index in range( kDisplayHeight ):
            if self.lines[ index ] != rhs.lines[ index ]: return True
        return False

    #
    # Determine if this Content instance has different right overlays than
    # another one.
    #
    def hasDifferentRightOverlays( self, rhs ):
        for index in range( kDisplayHeight ):
            if self.rightOverlays[ index ] != rhs.rightOverlays[ index ]: 
                return True
        return False

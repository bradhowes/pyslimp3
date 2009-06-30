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
from Display import *

#
# Renderer of Content contents to make a display. When the content is the same,
# but one or more lines are too long to show, this will scroll the lines to the
# left until all of the line has been displayed. It then loops back and shows
# the beginning of the line.
# 
# Supports a screensaver that is invoked after some configurable amount of time
# with no screen changes. After that interval, the display will go blank.
# Pressing a remote key or somehow causing the current display to change will
# remove the blanking.
#
class Animator( object ):

    kHoldCount = 8              # number of renders before animating
    kBlankingTimeout = 2 * 60   # 2 minutes of inactivity
    kBlankScreen = [ ' ' * kDisplayWidth ] * kDisplayHeight

    def __init__( self, screenTimeout = kBlankingTimeout ):
        self.content = None
        self.screenTimeout = screenTimeout
        self.reset()

    def reset( self ):
        self.offsets = [ 0 ] * kDisplayHeight
        self.atEnd = False
        self.holdCounter = Animator.kHoldCount
        self.unblankScreen()
   
    #
    # Apply new display content for animating. Resets animation values if the
    # screen content is different.
    #
    def setContent( self, content ):
        
        #
        # If the main content lines are different, reset any animation and
        # unblank the screen.
        #
        if content.hasDifferentLines( self.content ):
            self.content = content
            self.reset()
            self.shiftsNeeded = content.shiftsNeeded
            self.maxShift = max( content.shiftsNeeded )

        #
        # Lines are the same, but the right overlays are different, just
        # keep the blanker from taking effect.
        #
        elif content.hasDifferentRightOverlays( self.content ):
            self.unblankScreen()

        #
        # Both are the same. Blank after some number of seconds have passed.
        #
        elif not self.blanked:
            delta = datetime.now()
            delta -= self.blankingTimestamp
            if delta.seconds >= self.screenTimeout:
                self.blanked = True

    #
    # Unblank the screen, allowing updates to show
    #
    def unblankScreen( self ):
        self.blankingTimestamp = datetime.now()
        self.blanked = False

    #
    # Blank the screen, inhibiting content data from reaching the display
    #
    def blankScreen( self ):
        self.blanked = True

    #
    # Determine if the screeen should be blanked due to inactivity.
    #
    def isBlanking( self ): 
        return self.blanked
    
    #
    # Gererate output for the display, applying any animation necessary to show
    # long lines.
    #
    def render( self ):

        #
        # Just show a blank screen if there are no updates after N seconds
        #
        if self.blanked:
            return self.kBlankScreen

        #
        # Obtain a rendering from the current display content, using any
        # animation offsets we have.
        #
        output = self.content.render( self.offsets )
        if self.maxShift == 0:
            return output

        #
        # Decrement our hold counter. Once at zero, we will start animating.
        #
        self.holdCounter -= 1
        if self.holdCounter > 0:
            return output

        #
        # Scroll each line that needs it.
        #
        for index in range( kDisplayHeight ):
            shiftNeeded = self.shiftsNeeded[ index ]
            if shiftNeeded > 0:
                offset = self.offsets[ index ]
                if offset == shiftNeeded:

                    #
                    # Reached the end of this line. Are we the biggest line?
                    #
                    if shiftNeeded == self.maxShift:
                        if self.atEnd:

                            #
                            # We were frozen at the end. Scroll back to the
                            # beginning of the line.
                            #
                            self.atEnd = False
                            self.offsets = [ 0 ] * kDisplayHeight

                        else:

                            #
                            # We are at the end. Reset holdCounter to 'freeze'
                            # at the end.
                            #
                            self.atEnd = True
                            self.holdCounter = Animator.kHoldCount / 2
                            
                        #
                        # It is sound to break here since we already know that
                        # we are working with one of the longest lines.
                        #
                        break

                else:

                    #
                    # Increment the offset to scroll the line to the left.
                    #
                    offset += 1
                    self.offsets[ index ] = offset

        return output

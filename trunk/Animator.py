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
class Animator( object ):

    kHoldCount = 10             # Number of renders before animating

    def __init__( self, screenSaverClass, screenSaverTimeout ):
        self.content = None
        self.output = None
        self.screenSaverClass = screenSaverClass
        self.screenSaverTimeout = screenSaverTimeout
        self.reset()

    #
    # Install a new screen saver class to use, and invoke it if one is already
    # active.
    #
    def setScreenSaverClass( self, screenSaverClass ):
        self.screenSaverClass = screenSaverClass
        if self.screenSaver:
            self.screenSaver = screenSaverClass( self.output )

    #
    # Reset to known state and remove any active screen saver.
    #
    def reset( self ):
        self.offsets = [ 0 ] * kDisplayHeight
        self.atEnd = False
        self.holdCounter = Animator.kHoldCount
        self.removeScreenSaver()

    #
    # Apply new display content for animating. Resets animation values if the
    # screen content is different.
    #
    def setContent( self, content ):

        #
        # If the main content lines are different or the shifts needed to show
        # an entire line are different, reset the animation.
        #
        shiftsNeeded = content.shiftsNeeded
        if self.content is None or \
                content.hasDifferentLines( self.content ) or \
                self.shiftsNeeded != shiftsNeeded:
            self.reset()
            self.maxShift = max( shiftsNeeded )
            self.shiftsNeeded = shiftsNeeded
        #
        # If lines are the same but the overlays differ, just remove any active
        # screen saver.
        #
        elif content.hasDifferentRightOverlays( self.content ):
            self.removeScreenSaver()
        #
        # Lines are the same, as are the overlays. Check to see if we should
        # invoke a screen saver.
        #
        elif self.screenSaver is None:
            delta = datetime.now()
            delta -= self.activatingTimestamp
            if delta.seconds >= self.screenSaverTimeout:
                self.activateScreenSaver()
        self.content = content

    def activateScreenSaver( self ):
        self.screenSaver = self.screenSaverClass( self.output )

    def removeScreenSaver( self ):
        self.activatingTimestamp = datetime.now()
        self.screenSaver = None

    #
    # Determine if the screen saver is active
    #
    def screenSaverActivated( self ):
        return self.screenSaver is not None

    #
    # Gererate output for the display, applying any animation necessary to show
    # long lines.
    #
    def render( self ):

        if self.screenSaver:
            return self.screenSaver.render()

        #
        # Obtain a rendering from the current display content, using any
        # animation offsets we have.
        #
        self.output = output = self.content.render( self.offsets )
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
                            self.holdCounter = Animator.kHoldCount / 2

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
                    # Clamp to the amount needed to shift the line to the right
                    # and store.
                    #
                    offset += 2
                    self.offsets[ index ] = min( offset, shiftNeeded )

        return output

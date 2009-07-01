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

from time import time

#
# A Timer object contains a timestamp that indicates when it should fire, and a
# method to invoke when it is fired (from inside its fire() method). Note that
# the notifier object may be a method or an object that implements the __call__
# interface.
#
class Timer( object ):

    kFired = -1

    def __init__( self, next, when, notifier ):
        self.next = next
        self.when = when
        self.notifier = notifier

    #
    # If not already fired (or deactivated), invoke the notifier given in the
    # constructor. 
    #
    def fire( self ):
        if self.when != self.kFired:
            self.when = self.kFired
            self.notifier()

    def deactivate( self ):
        self.when = self.kFired
        

#
# Manager of active Timer objects. Maintains a linked list of Timer objects,
# ordered by their timestamp values. Periodically, one must invoke
# the processTimers() method to process the active Timer objects.
#
class TimerManager( object ):

    def __init__( self ):
        self.head = Timer( None, Timer.kFired, None )

    #
    # Create a new Timer object, add to the list of pending timers, and return
    # it to the caller. The delta parameter is the number of seconds in the
    # future when the timer should fire. The notifier parameter is a method to
    # invoke or an object that implements the __call__ interface.
    #
    def addTimer( self, delta, notifier ):
        
        #
        # Calculate the absolute time when the timer should fire.
        #
        when = time() + delta
        
        #
        # Insert at the appropriate place in the list to keep the firing times
        # ordered in increasing value.
        #
        pos = self.head
        while pos.next is not None and pos.next.when < when:
            pos = pos.next
        pos.next = Timer( pos.next, when, notifier )
        return pos.next

    #
    # Remove the indicated timer from the list of active timers.
    #
    def removeTimer( self, timer ):
        if timer is None:
            return
        timer.deactivate()
        pos = self.head
        while pos.next is not None:
            if pos.next == timer:
                pos.next = timer.next
                return
            pos = pos.next

    #
    # Process the list of active timers, executing the fire() method of each
    # one whose timestamp is older than the current time.
    #
    def processTimers( self ):
        now = time()
        timer = self.head.next

        #
        # Process timers until we reach one that has a timestamp in the future.
        #
        while timer is not None and timer.when <= now:
            self.head.next = timer.next
            timer.fire()
            timer = timer.next

    #
    # Remove all Timer objects. Below should be sufficient unless there was a
    # loop.
    #
    def reset( self ):
        self.head.next = None

    def dump( self ):
        pos = self.head.next
        while pos != None:
            print( pos.when, pos.client, pos.notifier )
            pos = pos.next

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

class Timer( object ):

    kFired = -1

    def __init__( self, next, when, client, notifier ):
        self.next = next
        self.when = when
        self.client = client
        self.notifier = notifier

    def fire( self ):
        if self.when != self.kFired:
            self.when = self.kFired
            if self.notifier:
                self.notifier()
            elif self.client:
                self.client.handleTimeout()

class TimerManager( object ):

    def __init__( self ):
        self.head = Timer( None, Timer.kFired, None, None )

    def addTimer( self, delta, client, notifier ):
        when = time() + delta
        pos = self.head
        while pos.next is not None and pos.next.when < when:
            pos = pos.next
        pos.next = Timer( pos.next, when, client, notifier )
        return pos.next

    def removeTimer( self, timer ):
        if timer is None:
            return
        timer.when = Timer.kFired
        pos = self.head
        while pos.next is not None:
            if pos.next == timer:
                pos.next = timer.next
                return
            pos = pos.next

    def removeClientTimers( self, client ):
        pos = self.head
        while pos.next is not None:
            timer = pos.next
            if timer.client == client:
                timer.when = Timer.kFired
                pos.next = timer.next
            pos = timer

    def processTimers( self ):
        now = time()
        timer = self.head.next
        while timer is not None and timer.when <= now:
            self.head.next = timer.next
            timer.fire()
            timer = timer.next

    def reset( self ):
        pos = self.head
        while pos.next is not None:
            tmp = pos.next.next
            pos.next.next = None
            pos.next = tmp
        print( 'self.head', self.head )

    def dump( self ):
        pos = self.head.next
        while pos != None:
            print( pos.when, pos.client, pos.notifier )
            pos = pos.next

#
# Copyright (C) 2009, 2010 Brad Howes.
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

#
# Key Constants
#
kDigit0 = '0'
kDigit1 = '1'
kDigit2 = '2'
kDigit3 = '3'
kDigit4 = '4'
kDigit5 = '5'
kDigit6 = '6'
kDigit7 = '7'
kDigit8 = '8'
kDigit9 = '9'
kArrowUp = 'arrowUp'
kArrowDown = 'arrowDown'
kArrowLeft = 'arrowLeft'
kArrowRight = 'arrowRight'
kRewind = 'rewind'
kFastForward = 'fastForward'
kChannelUp = 'channelUp'
kChannelDown = 'channelDown'
kDisplay = 'display'
kGuide = 'guide'
kMenuHome = 'menuHome'
kMute = 'mute'
kOK = 'ok'
kPause = 'pause'
kPIP = 'pip'
kPlay = 'play'
kPower = 'power'
kRecord = 'record'
kRepeat = 'repeat'
kSleep = 'sleep'
kStop = 'stop'
kVolumeDown = 'volumeDown'
kVolumeUp = 'volumeUp'

#
# Key Event Modifiers
#
kModFirst = 'ModFirst'          # Key seen for the first time
kModHeld = 'ModHeld'            # Key still down after kHoldPressThreshold
kModRepeat = 'ModRepeat'        # Key repeated
kModRelease = 'ModRelease'      # Key released
kModReleaseHeld = 'ModReleaseHeld' # Held key released

#
# Create a keyCode made up of a key and a modifier
#
def makeKeyCode( key, mod ): return key + '.' + mod

#
# Create a list of keyCode values, one for each provided modifier
#
def makeKeyCodes( key, mods ):
    if mods is None: mods = ( kModFirst, )
    elif type( mods ) not in ( list, tuple ):
        mods = ( mods, )
    return map( lambda a: key + '.' + a, mods )

#
# Converter of raw remote key events into keyCode values. The keyCode values
# are then handed to a notifier object via its processKeyCode() method for
# processing. A keyCode is a pairing of a key constant value (eg. kDigit0) and
# an event modifier (eg. kModFirst). The event modifiers describe where in time
# the key constant event took place:
#
#  kModFirst - the initial sighting of the key value
#  kModRepeat - the key value is still held down
#  kModHeld - the key value is pressed after kHoldPressThreshold seconds
#  kModRelease - the key is no longer down
#  kModReleaseHeld - a key that was down for kHoldPressThreshold is up
#
# Note that only one 'release' event is issued, kModRelease or kModReleaseHeld,
# depending on whether kModHeld was issued.
#

class KeyProcessor( object ):

    #
    # How often to check for a key release. This should be long enough to
    # eliminate false positives but short enough to stop repeated key events.
    # This is also how frequently a held-key will repeat an action.
    #
    # kReleaseCheckThreshold = 0.256 # seconds
    kReleaseCheckThreshold = 0.100 # seconds

    #
    # Number of calls to checkForRelease() before a button reports being held
    # down. Since checkForRelease() runs every kReleaseCheckThreshold, a button
    # must be held down for kHoldPressThreshold * kReleaseCheckThreshold
    # seconds before it begins repeating.
    #
    kHoldPressCount = 4
    
    #
    # Amount of time that must pass so that an incoming key message with the
    # same key code as the last message is treated as a separate key press, and
    # not a held key event.
    #
    kUniqueKeyPressTimeDelta = 100
    
    def __init__( self, timerManager, notifier ):
        self.timerManager = timerManager
        self.notifier = notifier
        self.releaseTimer = None
        self.reset( True )

    #
    # Reset the key processor to a known state. If there is an active
    # releaseTimer, we set the silenced flag but leave everything else alone,
    # and let the checkForRelease() method clean up for us. This is done so
    # that screen changes caused by remote commands won't inherit key release
    # or repeat events.
    #
    def reset( self, force = False ):
        if force or self.releaseTimer is None:
            self.silenced = False
            self.lastKey = None
            self.lastTimeStamp = None
            self.emittedHeldKey = False
            self.downCount = 0
        else:
            self.silenced = True

    #
    # Process a new raw key event from a remote controller. Depending on what
    # has taken place in the recent past, it may invoke the notify() one or
    # more times.
    #
    def process( self, timeStamp, key ):

	timeStamp = timeStamp / 100000.0

	# print( 'key:', key, 'timestamp:', timeStamp )
        #
        # Override timestamp from SliMP3 message. Makes an (gross?) assumption
        # that UDP latencies from the SliMP3 to us are low.
        #
        delta = 0
        if self.lastTimeStamp:
            delta = timeStamp - self.lastTimeStamp
            # print( 'timeStamp', timeStamp, timeStamp - self.lastTimeStamp )
        self.lastTimeStamp = timeStamp

        #
        # Same key but only if no gap in updates
        #
        if key == self.lastKey and delta < self.kUniqueKeyPressTimeDelta:

            self.pendingRelease = False

        else:

            #
            # If we have an active releaseTimer, manually fire it. Make sure
            # that it will think that the previous key was released.
            #
            if self.releaseTimer:
                self.pendingRelease = True
                self.releaseTimer.fire()
            else:
                self.reset( True )

            #
            # New key press.
            #
            self.lastKey = key
            self.downCount = 0
            self.lastTimeStamp = timeStamp
            self.startReleaseTimer()
            self.notify( kModFirst )

    #
    # Start a timer that will invoke checkForRelease() after
    # kReleaseCheckThreshold seconds.
    #
    def startReleaseTimer( self ):
        self.pendingRelease = True
        self.releaseTimer = self.timerManager.addTimer( 
            self.kReleaseCheckThreshold, self.checkForRelease )

    #
    # Check if a release event has occured and if so notify the notifier.
    #
    def checkForRelease( self ):

        #
        # If an event was received since we last checked, try again.
        #
        if not self.pendingRelease:
            self.startReleaseTimer()

            #
            # Keep track of how many times we've been called for this key
            # event, and emit 'held' and repeat messages when enough time has
            # passed.
            #
            downCount = self.downCount + 1
            self.downCount = downCount
            if downCount == self.kHoldPressCount:
                self.notify( kModHeld )
            elif downCount > self.kHoldPressCount:
                self.notify( kModRepeat )
            return

        #
        # Honor the silenced attribute so that we don't emit keCode events
        # inside a new screen.
        #
        if not self.silenced:
            if self.emittedHeldKey:
                self.notify( kModReleaseHeld )
            else:
                self.notify( kModRelease )

        #
        # Make sure reset
        #
        self.reset( True )

    #
    # Notify the notifier object that a new keyCode event has taken place.
    #
    def notify( self, modifier ):
        keyCode = makeKeyCode( self.lastKey, modifier )
        # print( 'notify', keyCode )
        self.notifier.processKeyCode( keyCode )

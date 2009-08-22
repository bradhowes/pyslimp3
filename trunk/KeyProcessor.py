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
    #
    kReleaseCheckThreshold = 0.256 # seconds

    #
    # Minimum amount of time in seconds a key must be held down in order for it
    # to be considered 'held'
    #
    kHoldPressThreshold = 0.512 # seconds

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
            self.firstTimeStamp = None
            self.lastTimeStamp = None
            self.emittedHeldKey = False
        else:
            self.silenced = True

    #
    # Process a new raw key event from a remote controller. Depending on what
    # has taken place in the recent past, it may invoke the notify() one or
    # more times.
    #
    def process( self, timeStamp, key ):

        #
        # Override timestamp from SliMP3 message. Makes an (gross?) assumption
        # that UDP latencies from the SliMP3 to us are low.
        #
        timeStamp = datetime.now()

        #
        # Same key?
        #
        if key == self.lastKey:

            #
            # Update the timestamp so that checkForRelease() will keep running.
            #
            self.lastTimeStamp = timeStamp

            #
            # Calculate how long the key has been held down for.
            #
            delta = timeStamp - self.firstTimeStamp
            delta = delta.seconds + delta.microseconds / 1000000.0

            #
            # If we have yet to emit the 'kModHeld' modifier, check to see if
            # we've held the key down long enough to emit it.
            #
            if not self.emittedHeldKey:
                if delta >= self.kHoldPressThreshold:
                    self.emittedHeldKey = True
                    self.notify( kModHeld )
            else:

                #
                # We've already emitted a 'held' event, so now emit 'repeat'
                # events.
                #
                self.notify( kModRepeat )

        else:
            
            #
            # If we have an active releaseTimer, manually fire it. Make sure
            # that it will think that the previous key was released.
            #
            if self.releaseTimer:
                self.lastTimeStamp = self.releaseTimeStamp
                self.releaseTimer.fire()
            else:
                self.reset( True )

            #
            # New key press.
            #
            self.lastKey = key
            self.firstTimeStamp = timeStamp
            self.lastTimeStamp = timeStamp
            self.startReleaseTimer( timeStamp )
            self.notify( kModFirst )

    #
    # Start a timer that will invoke checkForRelease() after
    # kReleaseCheckThreshold seconds.
    #
    def startReleaseTimer( self, timeStamp ):
        self.releaseTimeStamp = timeStamp
        self.releaseTimer = self.timerManager.addTimer( 
            self.kReleaseCheckThreshold, self.checkForRelease )

    #
    # Check if a release event has occured and if so notify the notifier.
    #
    def checkForRelease( self ):

        #
        # If an event was received since we last checked, try again.
        #
        if self.lastTimeStamp != self.releaseTimeStamp:
            self.startReleaseTimer( self.lastTimeStamp )
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
        print( 'notify', keyCode )
        self.notifier.processKeyCode( keyCode )
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
kShuffle = 'shuffle'
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
    # The timestamp values in the key messages have a frequency of 625 kHz
    #
    kTicsPerSecond = 625000.0
    
    #
    # Maximum timestamp value in seconds
    #
    kMaxTimeStamp = 0xFFFFFFFF / kTicsPerSecond

    #
    # Minimum amount of time in seconds a key must be held down in order for it
    # to be considered for processing.
    #
    kMinPressThreshold = 0.128
    
    #
    # Minimum amount of time in seconds a key must be held down in order for it
    # to be considered 'held'
    #
    kHoldPressThreshold = 0.512

    def __init__( self, timerManager, notifier ):
        self.timerManager = timerManager
        self.notifier = notifier
        self.releaseTimer = None
        self.lastTimeStamp = None
        self.reset()

    #
    # Reset the key processor to a known state.
    #
    def reset( self ):
        self.notifyTimeStamp = None
        self.emittedHeldKey = False
        if self.releaseTimer:
            self.silenced = True
        else:
            self.silenced = False
            self.lastKey = None

    #
    # Process a new raw key event from a remote controller. Depending on what
    # has taken place in the recent past, it may invoke the notify() one or
    # more times.
    #
    def process( self, timeStamp, key ):

        #
        # Convert 625 kHz counter value into seconds.
        #
        timeStamp = timeStamp / self.kTicsPerSecond
        if self.lastTimeStamp is None:
            self.lastTimeStamp = timeStamp
            return

        #
        # Same key?
        #
        if key == self.lastKey and self.notifyTimeStamp:

            #
            # Update the timestamp so that checkForRelease() will keep running.
            #
            self.lastTimeStamp = timeStamp

            #
            # Calculate how long the key has been held down for.
            #
            delta = timeStamp - self.notifyTimeStamp
            if delta < 0:
                delta += self.kMaxTimeStamp

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

        elif self.releaseTimer is None:
            self.reset()
            self.lastKey = key
            self.lastTimeStamp = timeStamp
            self.startReleaseTimer( timeStamp, 2 * self.kMinPressThreshold )
            self.notify( kModFirst )

    #
    # Start a timer that will invoke checkForRelease() after kMinPressThreshold
    # seconds.
    #
    def startReleaseTimer( self, timeStamp, delta ):
        self.releaseTimeStamp = timeStamp
        self.releaseTimer = self.timerManager.addTimer( delta, 
                                                        self.checkForRelease )

    #
    # Check if a release event has occured and if so notify the notifier.
    #
    def checkForRelease( self ):

        #
        # If an event was received since we last checked, try again.
        #
        if self.lastTimeStamp != self.releaseTimeStamp:
            self.startReleaseTimer( self.lastTimeStamp, 
                                    self.kMinPressThreshold )
            return

        if self.emittedHeldKey:
            self.notify( kModReleaseHeld )
        else:
            self.notify( kModRelease )

        self.releaseTimer = None
        self.reset()

    #
    # Notify the notifier object that a new keyCode event has taken place.
    #
    def notify( self, modifier ):
        keyCode = makeKeyCode( self.lastKey, modifier )
        print 'notify', keyCode
        self.notifier.processKeyCode( keyCode )
        self.notifyTimeStamp = self.lastTimeStamp

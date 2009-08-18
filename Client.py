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

import socket
from datetime import datetime, timedelta

from Animator import Animator
from Browser import Browser
from Display import *
from KeyProcessor import *
from PlaybackDisplay import PlaybackDisplay
from TopBrowser import TopBrowser
from VFD import VFD

#
# Representation of the state of a remote SLIMP3 device. Manages a socket that
# communicates to the remote device via UDP messages.
#
class Client( object ):

    #
    # Frequency of display updates
    #
    kRefreshInterval = 0.25     # seconds
    
    #
    # How long to wait before we revert to a PlaybackDisplay display generator
    # when iTunes is playing.
    #
    kPlaybackDisplayRestoreInterval = 10.0 # seconds

    #
    # Number of seconds to show an overlay screen before reverting to the
    # normal display generator.
    #
    kOverlayDuration = 3.0      # seconds

    def __init__( self, server, addr, state ):
        self.server = server
        self.hardwareAddress = addr
        self.isOn = False
        self.brightness = VFD.kMaxBrightness
        self.iTunes = server.iTunes
        self.keyProcessor = KeyProcessor( server, self )
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.lastHardwareMessageReceived = datetime.now()
        self.linesGenerator = None
        self.overlayGenerator = None
        self.overlayTimer = None
        self.refreshTimer = None
        self.lastKeyTimeStamp = datetime.now() - timedelta( seconds = 1000 )
        self.animator = Animator()
        self.vfd = VFD( self.brightness )
        self.fillKeyMap()
        self.playbackFormatterIndex = 0
        if state:
            self.brightness = state[ 'brightness' ]
            self.isOn = state[ 'isOn' ]
            self.playbackFormatterIndex = state.get( 'playbackFormatterIndex',
                                                     0 )
        if self.isOn:
            self.powerOn()
        else:
            self.powerOff()
        self.refreshDisplay()

    def getState( self ):
        settings = {}
        settings[ 'brightness' ] = self.brightness
        settings[ 'isOn' ] = self.isOn
        settings[ 'playbackFormatterIndex' ] = self.playbackFormatterIndex
        return settings

    #
    # Create the mapping from key codes to methods for global methods, those
    # that do not necessarily pertain to a particular display generator.
    #
    def fillKeyMap( self ):
        self.keyMap = keyMap = {}
        for each in (

            #
            # Volume control
            #
            ( kVolumeUp, self.volumeUp, ( kModFirst, kModRepeat ) ),
            ( kVolumeDown, self.volumeDown, ( kModFirst, kModRepeat ) ),

            #
            # Display brightnes
            #
            ( kChannelUp, self.brightnessUp, ( kModFirst, kModRepeat ) ),
            ( kChannelDown, self.brightnessDown, ( kModFirst, kModRepeat ) ),

            #
            # Global state manipulation
            #
            ( kMute, self.toggleMute ),
            ( kShuffle, self.toggleShuffle ),
            ( kRepeat, self.toggleRepeat ),
            ( kPower, self.togglePower ),

            #
            # Display views
            #
            ( kDisplay, self.showPlaying ),
            ( kMenuHome, self.showTopBrowser ),
            
            #
            # Simple iTunes control
            #
            ( kStop, self.iTunes.stop ),
            ( kPause, self.iTunes.pause ),
            ):

            key = each[ 0 ]
            proc = each[ 1 ]
            mods = None
            if len( each ) == 3: 
                mods = each[ 2 ]

            for keyCode in makeKeyCodes( key, mods ):
                keyMap[ keyCode ] = proc

    #
    # Update the hearbeat timestamp used by isStale() to determine if a client
    # is no longer among the living.
    #
    def touch( self ):
        self.lastHardwareMessageReceived = datetime.now()

    #
    # Determine if we have not received a message in the last 60 seconds.
    #
    def isStale( self, when ):
        delta = when - self.lastHardwareMessageReceived
        return delta.seconds > 60

    #
    # Close the client connection
    #
    def close( self ):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        self.server.removeTimer( self.refreshTimer )
        self.server.removeTimer( self.overlayTimer )
        del self.keyProcessor
        self.keyProcessor = None

    #
    # Install a DisplayGenerator object as the source of our display. Clears
    # out any existing overlay generator. Refreshes the display.
    #
    def setLinesGenerator( self, generator ):
        
        #
        # Reset the key processor so that the new display generator won't
        # inherit any outstanding keyCode events.
        #
        self.keyProcessor.reset()
        self.linesGenerator = generator

        #
        # If there is an existing overlay screen generator, remove it and the
        # timer used to remove it.
        #
        if self.overlayTimer:
            self.overlayTimer.deactivate()
            self.overlayTimer = None
            self.overlayGenerator = None
        self.emitDisplay()

    #
    # Install a temporary overlay screen generator as the source of our
    # display. Installs a timer to remove it after 'duration' seconds.
    #
    def setOverlayGenerator( self, overlayGenerator ):
        if self.overlayGenerator is None:
            
            #
            # Reset the key processor so that the new display generator won't
            # inherit any outstanding keyCode events.
            #
            self.keyProcessor.reset()

        self.overlayGenerator = overlayGenerator
        self.emitDisplay()

        #
        # Install a timer to remove the overlay screen generator, removing any
        # existing timer.
        #
        if self.overlayTimer:
            self.overlayTimer.deactivate()
        self.overlayTimer = self.server.addTimer( self.kOverlayDuration,
                                                  self.clearOverlay )

    #
    # Remove any overlay screen generator.
    #
    def clearOverlay( self ):
        if self.overlayGenerator:

            #
            # Reset the key processor so that the normal display generator
            # won't inherit any outstanding keyCode events.
            #
            self.keyProcessor.reset()
            self.overlayGenerator = None
            if self.overlayTimer:
                self.overlayTimer.deactivate()
                self.overlayTimer = None
            self.emitDisplay()

    #
    # Timer event handler that periodically generates a new display and sends
    # it out. 
    #
    def refreshDisplay( self ):
        
        #
        # If iTunes is currently playing and the current display generator is
        # not a PlaybackDisplay, see if we should force it to be.
        #
        if self.iTunes.isPlaying() and \
                not isinstance( self.linesGenerator, PlaybackDisplay ):
            delta = datetime.now() - self.lastKeyTimeStamp
            if delta.seconds > self.kPlaybackDisplayRestoreInterval:
                self.setLinesGenerator( 
                    PlaybackDisplay( self.iTunes, self.linesGenerator,
                                     self.playbackFormatterIndex ) )
        self.emitDisplay()

        #
        # Install a new timer for the next update.
        #
        self.server.removeTimer( self.refreshTimer )
        self.refreshTimer = self.server.addTimer( self.kRefreshInterval, 
                                                  self.refreshDisplay )

    #
    # Generate a new display and send it to the client
    #
    def emitDisplay( self ):
        if self.socket is None:
            return
        if self.overlayGenerator:
            content = self.overlayGenerator.generate()
        else:
            content = self.linesGenerator.generate()

        #
        # Pass the content generated by the display generator to our animator
        # for rendering. Pass the animated result to the VFD device for
        # encoding. Emit the encoded result to the SLIMP3 device.
        #
        self.animator.setContent( content )
        data = self.vfd.build( self.animator.render() )

        try:
            rc = self.socket.sendto( data, self.hardwareAddress )
            if rc != len( data ):
                print( '*** failed to send', len( data ), 'bytes -', rc )
        except socket.error:
            print( '*** failed to send to client', self.hardwareAddress )

    #
    # Process raw IR key event from client. Let the KeyProcessor instance
    # translate to keyCode values and call us back via processKeyCode() when
    # appropriate.
    #
    def processKeyEvent( self, timeStamp, key ):
        self.lastKeyTimeStamp = datetime.now()
        if self.animator.screenSaverActivated():
            self.animator.removeScreenSaver()
            self.emitDisplay()
        else:
            self.keyProcessor.process( timeStamp, key )

    #
    # Callback invoked by KeyProcessor when it has a valid keyCode event to
    # process. Allow active screen generator objects to process the keyCode,
    # and if they don't handle it, attempt to ourselves.
    #
    def processKeyCode( self, keyCode ):

        #
        # If there is an temporary overlay display, see if it can process the
        # keyCode. Otherwise, let the current display generator have a crack at
        # it.
        #
        if self.overlayGenerator:
            generator = self.overlayGenerator.processKeyCode( keyCode )
        else:
            generator = self.linesGenerator.processKeyCode( keyCode )

        #
        # If not None, the key event was handled. Possibly install a new
        # display generator.
        #
        if generator:
            if generator.isOverlay():
                
                #
                # Install a temporary overlay display. Note that always
                # install, even for the same overlay generator in order to
                # reset the overlay timer.
                #
                self.setOverlayGenerator( generator )

            else:

                #
                # Normal display. Only update if it is different.
                #
                if generator != self.linesGenerator or self.overlayGenerator:
                    self.setLinesGenerator( generator )
                else:
                    self.emitDisplay()

        #
        # Last-chance key event processing. Look to see if we can handle it.
        #
        else:
            proc = self.keyMap.get( keyCode )
            if proc:
                proc()

    #
    # Volume control methods
    #
    def volumeUp( self ): self.changeVolume( 1 )
    def volumeDown( self ): self.changeVolume( -1 )
    def changeVolume( self, delta ):
        self.iTunes.adjustVolume( delta )
        self.setOverlayGenerator( VolumeGenerator( self.iTunes ) )

    #
    # Brightness control methods
    #
    def brightnessUp( self ):   
        self.vfd.changeBrightness( 1 )
        self.brightness = self.vfd.getBrightness()

    def brightnessDown( self ): 
        self.vfd.changeBrightness( -1 )
        self.brightness = self.vfd.getBrightness()

    #
    # Toggle iTUnes MUTE state
    #
    def toggleMute( self ):
        self.iTunes.toggleMute()
        self.setOverlayGenerator( MuteStateGenerator( self.iTunes ) )

    #
    # Toggle iTUnes shuffle state for a playlist
    #
    def toggleShuffle( self ):
        self.iTunes.toggleShuffle()
        self.setOverlayGenerator( ShuffleStateGenerator( self.iTunes ) )

    #
    # Cycle throught the iTunes repeat state for a playlist
    #
    def toggleRepeat( self ):
        self.iTunes.toggleRepeat()
        self.setOverlayGenerator( RepeatStateGenerator( self.iTunes ) )

    #
    # Toggle the 'power' button, showing a clock display ala SLIMP3 when the
    # power is 'off'.
    #
    def togglePower( self ):
        if self.isOn == False:
            self.powerOn()
        else:
            self.powerOff()

    def powerOn( self ):
        self.isOn = True
        browser = TopBrowser( self.iTunes )
        track = self.iTunes.getCurrentTrack()
        if track is None:
            generator = browser
        else:
            generator = PlaybackDisplay( self.iTunes, browser, 
                                         self.playbackFormatterIndex )
        self.setLinesGenerator( generator )

    def powerOff( self ):
        self.isOn = False
        self.setLinesGenerator( ClockGenerator() )
        try:
            self.iTunes.stop()
        except:
            pass

    #
    # Install a PlaybackDisplay screen generator if not currently active.
    #
    def showPlaying( self ):
        if not isinstance( self.linesGenerator, PlaybackDisplay ):
            track = self.iTunes.getCurrentTrack()
            if track is not None:
                self.setLinesGenerator(
                    PlaybackDisplay( self.iTunes, self.linesGenerator,
                                     self.playbackFormatterIndex ) )
        else:
            self.linesGenerator.nextPlayerPositionFormatter()
            self.playbackFormatterIndex = \
                self.linesGenerator.getFormatterIndex()

    #
    # Install a TopBrowser screen generator.
    #
    def showTopBrowser( self ):
        if not isinstance( self.linesGenerator, TopBrowser ):
            self.setLinesGenerator( TopBrowser( self.iTunes ) )

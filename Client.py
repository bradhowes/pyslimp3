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

import socket
from datetime import datetime, timedelta

from Animator import kAnimators
from Browser import Browser
from Display import *
from KeyProcessor import *
from PlaybackDisplay import PlaybackDisplay
from PlaylistBrowser import PlaylistBrowser
from ScreenSavers import kScreenSavers
from TopBrowser import TopBrowser
from VFD import VFD

#
# Representation of the state of a remote SLIMP3 device. Manages a socket that
# communicates to the remote device via UDP messages. There is one Client
# object per SLiMP3 device found on the network.
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

    def __init__( self, server, addr, settings ):
        self.server = server
        self.hardwareAddress = addr
        self.settings = settings
        self.iTunes = server.iTunes
        
        #
        # Create a new key event processor to handle remote control messages.
        # When a key event occurs, KeyProcessor will invoke our
        # processKeyCode() method.
        #
        self.keyProcessor = KeyProcessor( server, self )
        
        #
        # Create a new socket to use for sending out UDP messages to the SLiMP3
        # device or simulator.
        #
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        
        #
        # Maintain a timestamp of the last messages received from a SLiMP3
        # device or simulator so that we can detect when the device disappears.
        #
        self.lastHardwareMessageReceived = datetime.now()
        
        #
        # Normal display generator in use by the client
        #
        self.linesGenerator = None

        #
        # Overlay display generator for temporary displays such as volume
        # control or ratings.
        #
        self.overlayGenerator = None
        
        #
        # When an overlay generator is active, this is a timer that will remove
        # the overlay after kOverlayDuration seconds
        #
        self.overlayTimer = None
        
        #
        # Timer used to refresh the SLiMP3 display.
        #
        self.refreshTimer = None

        #
        # Time when the user last pressed a key on the remote. Used to
        # determine when to revert to a PlaybackDisplay display after the user
        # has moved to another display using the remote control.
        #
        self.lastKeyTimeStamp = datetime.now() - timedelta( seconds = 1000 )

        #
        # Create a new display animator to use to render Content objects from
        # the active display generator.
        #
        self.makeAnimator()

        #
        # Create a new VFD interface used to generate appropriate 'l' type
        # messages for the SLiMP3 device.
        #
        self.vfd = VFD( settings.getBrightness() )

        #
        # Install the key map for this Client, default actions for remote keys
        # not handled by the active or overlay display generator.
        #
        self.fillKeyMap()
        
        #
        # Put the SLiMP3 device in the same on/off state it was in when last
        # seen.
        #
        if settings.getIsOn():
            self.powerOn()
        else:
            self.powerOff()
            
        #
        # Force a dislay on the device.
        #
        self.refreshDisplay()

    def setHardwareAddress( self, addr ):
        self.hardwareAddress = addr

    #
    # Obtain the Settings object for this client
    #
    def getSettings( self ): return self.settings

    #
    # Determine if the Settings object is dirty and needs to be saved to disk.
    #
    def settingsAreDirty( self ):
        return self.settings.isDirty()

    #
    # Obtain the appscript object connected to iTunes.
    #
    def getSource( self ): return self.iTunes

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
            ( kOK, self.toggleShuffle ),
            ( kRepeat, self.toggleRepeat ),
            ( kPower, self.togglePower ),

            #
            # Display views
            #
            ( kDisplay, self.showPlaying ),
            ( kMenuHome, self.showTopBrowser ),
            ( kSleep, self.activateScreenSaver ),
            ( kRecord, self.showTargetPlaylist ),

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
            if self.overlayGenerator.prevLevel:
                self.setLinesGenerator( self.overlayGenerator.prevLevel )
                return

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
                    PlaybackDisplay( self, self.linesGenerator ) )
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
        
        #
        # If powered off, don't process any key but the kPower button
        #
        if not self.settings.getIsOn() and key != kPower:
            print( 'ignoring', key )
            return

        #
        # If a screen saver is active, just eat the key event and get rid of
        # the screen saver.
        #
        if self.animator.screenSaverActivated():
            self.animator.removeScreenSaver()
            self.emitDisplay()
            self.keyProcessor.reset()
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
    def volumeUp( self ): self.changeVolume( 5 )
    def volumeDown( self ): self.changeVolume( -5 )

    def changeVolume( self, delta ):
        extra = self.iTunes.getVolume() % delta
        self.iTunes.adjustVolume( delta - extra )
        self.setOverlayGenerator( 
            VolumeGenerator( self, self.linesGenerator ) )

    #
    # Increase brightness
    #
    def brightnessUp( self ):   
        self.vfd.changeBrightness( 1 )
        self.settings.setBrightness( self.vfd.getBrightness() )

    #
    # Decrease brightness
    #
    def brightnessDown( self ): 
        self.vfd.changeBrightness( -1 )
        self.settings.setBrightness( self.vfd.getBrightness() )

    #
    # Toggle iTunes mute state
    #
    def toggleMute( self ):
        self.iTunes.toggleMute()
        self.setOverlayGenerator( 
            MuteStateGenerator( self, self.linesGenerator ) )

    #
    # Toggle iTunes shuffle state for a playlist
    #
    def toggleShuffle( self ):
        self.iTunes.toggleShuffle()
        self.setOverlayGenerator( 
            ShuffleStateGenerator( self, self.linesGenerator ) )

    #
    # Cycle throught the iTunes repeat state for a playlist: off, all songs,
    # one song.
    #
    def toggleRepeat( self ):
        self.iTunes.toggleRepeat()
        self.setOverlayGenerator( 
            RepeatStateGenerator( self, self.linesGenerator ) )

    #
    # Toggle the 'power' button, showing a clock display ala SLIMP3 when the
    # power is 'off'.
    #
    def togglePower( self ):
        if self.settings.getIsOn() == False:
            self.powerOn()
        else:
            self.powerOff()

    #
    # Turn 'on' the SLiMP3 device, removing the clock display and showing the
    # current track using PlaybackDisplay or the TopBrowser display generator
    # depending on whether there is an active track.
    #
    def powerOn( self ):
        self.settings.setIsOn( True )
        browser = TopBrowser( self )
        track = self.iTunes.getCurrentTrack()
        if track is None:
            generator = browser
        else:
            generator = PlaybackDisplay( self, browser )
        self.setLinesGenerator( generator )

    #
    # Turn 'off' the SLiMP3 device, showing a clock display, just like the
    # original server software.
    #
    def powerOff( self ):
        self.settings.setIsOn( False )
        self.setLinesGenerator( ClockGenerator( self ) )
        try:
            self.iTunes.stop()
        except:
            pass

    #
    # Install a PlaybackDisplay screen generator if not currently active.
    #
    def showPlaying( self ):
        if self.overlayGenerator:
            self.clearOverlay()
            return
        if not isinstance( self.linesGenerator, PlaybackDisplay ):
            playlist = self.iTunes.getActivePlaylist()
            if playlist.getTrackCount() > 0:
                self.setLinesGenerator(
                    PlaybackDisplay( self, self.linesGenerator ) )

    #
    # Show a TopBrowser screen generator.
    #
    def showTopBrowser( self ):
        if not isinstance( self.linesGenerator, TopBrowser ):
            self.setLinesGenerator( TopBrowser( self ) )

    #
    # Show a PlaylistBrowser screen generator, showing the current target
    # playlist for REC operations.
    #
    def showTargetPlaylist( self ):
        if not isinstance( self.linesGenerator, PlaylistBrowser ):
            self.setLinesGenerator( 
                PlaylistBrowser( self, self.linesGenerator ) )

    #
    # Set the index of the screen saver to use. Updates the current Animator
    # object to use the new screen saver setting.
    #
    def setScreenSaverIndex( self, value ):
        self.settings.setScreenSaverIndex( value )
        self.animator.setScreenSaverClass( kScreenSavers[ value ] )

    #
    # Invoke the current screen saver.
    #
    def activateScreenSaver( self ):
        self.animator.activateScreenSaver()

    #
    # Set the idex of the Animator class to use, and use it.
    #
    def setAnimatorIndex( self, value ):
        self.settings.setAnimatorIndex( value )
        self.makeAnimator()

    def makeAnimator( self ):
        self.animator = kAnimators[ self.settings.getAnimatorIndex() ](
            kScreenSavers[ self.settings.getScreenSaverIndex() ],
            self.settings.getScreenSaverTimeout() )

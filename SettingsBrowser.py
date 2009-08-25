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

from Animator import kAnimators
from Browser import Browser
from Content import Content
from Display import *
from DynamicBrowser import DynamicBrowser, DynamicEntry
from KeyProcessor import *
from ScreenSavers import kScreenSavers

class NotificationDisplay( OverlayDisplay ):
    
    def __init__( self, client, prevLevel, line1, line2 = '' ):
        OverlayDisplay.__init__( self, client, prevLevel )
        self.line1 = centerAlign( line1 )
        self.line2 = centerAlign( line2 )

    def generate( self ):
        return Content( [ self.line1, self.line2 ] )

class SettingsBrowser( Browser ):

    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kArrowRight, ( kModFirst, ), self.install )
        self.addKeyMapEntry( kOK, ( kModFirst, ), self.install )

    def generateWith( self, obj ):
        return Content( [ self.kTitle, self.getDisplayName( obj ) ],
                        [ self.getIndexOverlay(), '' ] )

    def install( self ):
        self.updateSetting()
        return NotificationDisplay( self.client, self.prevLevel,
                                    self.kNotification )

    def updateSetting( self ):
        raise NotImplementedError, 'setSetting'

class ScreenSaverBrowser( SettingsBrowser ):
    kTitle = 'Screen Savers'
    kNotification = 'Screen saver changed'
    def getCollection( self ): return kScreenSavers
    def getDisplayValue( self, obj ): return obj.kName
    def updateSetting( self ): self.client.setScreenSaverIndex( self.index )

class AnimatorBrowser( SettingsBrowser ):
    kTitle = 'Animators'
    kNotification = 'Animator changed'
    def getCollection( self ): return kAnimators
    def getDisplayValue( self, obj ): return obj.kName
    def updateSetting( self ): self.client.setAnimatorIndex( self.index )

class ScreenSaverSetting( DynamicEntry, SettingsBrowser ):

    def makeContent( self, browser ):
        return [ 'Current Screen Saver:', kScreenSavers[ self.index ].kName ]

    def makeNextLevel( self, browser ):
        index = browser.client.getSettings().getScreenSaverIndex()
        return ScreenSaverBrowser( browser.client, browser, index )

class AnimatorSetting( DynamicEntry ):

    def makeContent( self, browser ):
        index = browser.client.getSettings().getAnimatorIndex()
        return [ 'Current Animator:', kAnimators[ index ].kName ]

    def makeNextLevel( self, browser ):
        index = browser.client.getSettings().getAnimatorIndex()
        return AnimatorBrowser( browser.client, browser, index )

class SettingsBrowser( DynamicBrowser ):

    def __init__( self, client, prevLevel ):
        DynamicBrowser.__init__( self, client, prevLevel,
                                 ( ScreenSaverSetting(),
                                   AnimatorSetting(), ) )

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

#
# Base class for setting browsers that operate on a list of values. Derived
# classes must implement the install() method that shou.d apply the new
# configuration setting value.
#
class ChoiceSetting( Browser ):

    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kArrowRight, ( kModFirst, ), self.install )
        self.addKeyMapEntry( kOK, ( kModFirst, ), self.install )

    def generateWith( self, obj ):
        return Content( [ self.kTitle, self.getDisplayValue( obj ) ],
                        [ self.getIndexOverlay(), '' ] )

    def install( self ):
        self.updateSetting()
        return NotificationDisplay( self.client, self.prevLevel,
                                    self.kNotification )

    def updateSetting( self ):
        raise NotImplementedError, 'setSetting'

#
# ChoiceSetting derivative that browses a list of screen saver names.
#
class ScreenSaverBrowser( ChoiceSetting ):
    kTitle = 'Screen Savers'
    kNotification = 'Screen saver changed'
    def getCollection( self ): return kScreenSavers
    def getDisplayValue( self, obj ): return obj.kName
    def updateSetting( self ): self.client.setScreenSaverIndex( self.index )

#
# DynamicEntry derivative that shows the current screen saver setting, and can
# create a new ScreenSaverBrowser object to choose a new setting.
#
class ScreenSaverSetting( DynamicEntry ):

    def makeContent( self, browser ):
        index = browser.client.getSettings().getScreenSaverIndex()
        return [ 'Current Screen Saver:', kScreenSavers[ index ].kName ]

    def makeNextLevel( self, browser ):
        index = browser.client.getSettings().getScreenSaverIndex()
        return ScreenSaverBrowser( browser.client, browser, index )

#
# ChoiceSetting derivative that browses a list of display animator names.
#
class AnimatorBrowser( ChoiceSetting ):
    kTitle = 'Animators'
    kNotification = 'Animator changed'
    def getCollection( self ): return kAnimators
    def getDisplayValue( self, obj ): return obj.kName
    def updateSetting( self ): self.client.setAnimatorIndex( self.index )

#
# DynamicEntry derivative that shows the current display animation and can
# create a new AnimatorBrowser to choose a new setting.
#
class AnimatorSetting( DynamicEntry ):

    def makeContent( self, browser ):
        index = browser.client.getSettings().getAnimatorIndex()
        return [ 'Current Animator:', kAnimators[ index ].kName ]

    def makeNextLevel( self, browser ):
        index = browser.client.getSettings().getAnimatorIndex()
        return AnimatorBrowser( browser.client, browser, index )

#
# Browser for user configuration settings.
#
class SettingsBrowser( DynamicBrowser ):

    def __init__( self, client, prevLevel ):
        DynamicBrowser.__init__( self, client, prevLevel,
                                 ( ScreenSaverSetting(),
                                   AnimatorSetting(), ) )

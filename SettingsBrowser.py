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

class ScreenSaverBrowser( Browser ):

    def fillKeyMap( self ):
        Browser.fillKeyMap( self )
        self.addKeyMapEntry( kArrowRight, ( kModFirst, ), self.install )
        self.addKeyMapEntry( kOK, ( kModFirst, ), self.install )

    def getCollection( self ):
        return kScreenSavers

    def generateWith( self, obj ):
        return Content( [ 'Screen Savers',
                          obj.name ],
                        [ self.getIndexOverlay(),
                          '' ] )

    def install( self ):
        self.client.setScreenSaverIndex( self.index )
        return NotificationDisplay( self.client, self.prevLevel,
                                    "Screen saver changed" )

class ScreenSaverSetting( DynamicEntry ):

    def makeContent( self, browser ):
        index = browser.client.getSettings().getScreenSaverIndex()
        return [ 'Current Screen Saver:', 
                 kScreenSavers[ index ].name ]

    def makeNextLevel( self, browser ):
        index = browser.client.getSettings().getScreenSaverIndex()
        return ScreenSaverBrowser( browser.client, browser, index )

class SettingsBrowser( DynamicBrowser ):

    def __init__( self, client, prevLevel ):
        DynamicBrowser.__init__( self, client, prevLevel,
                                 ( ScreenSaverSetting(), ) )

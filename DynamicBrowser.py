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

class DynamicEntry( object ):
    def makeContent( self, browser ): 
        raise NotImplementedError, 'makeContent'
    def makeNextLevel( self, browser ): 
        raise NotImplementedError, 'makeNextLevel'

#
# Specialization of Browser that shows a collection of items which are
# dynamically generated, not statically. Each item in the collection must
# conform to the DynamicEntry interface defined above, with a makeContent()
# routine and a makeNextLevel() routine. The former is invoked to generate the
# content to show on the SliMP3 device, while the latter is called to generate
# a new Display object when the user presses the kArrowRight button on the
# remote control.
#
class DynamicBrowser( Browser ):

    def __init__( self, client, prevLevel, collection ):
        Browser.__init__( self, client, prevLevel )
        self.collection = collection

    #
    # Implementation of Browser interface. Returns held collection object
    #
    def getCollection( self ): return self.collection

    #
    # Obtain the display content for the current index.
    #
    def generateWith( self, obj ): 
        return Content( obj.makeContent( self ) )

    #
    # Go down a level and show a different browser.
    #
    def makeNextLevel( self ):
        return self.getCurrentObject().makeNextLevel( self )

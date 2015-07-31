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

from Content import *
from Display import *
from KeyProcessor import *

#
# Generic YES/NO, OK/Cancel confirmation dialog
#
class YesNoEntry( OverlayDisplay ):

    def __init__( self, client, prevLevel, title, acceptor = None,
                  yesTitle = 'YES', noTitle = 'NO' ):
        DisplayGenerator.__init__( self, client, prevLevel ) 
        self.line1 = title
        self.line2 = u'1:' + yesTitle + u'  3:' + noTitle
        self.acceptor = acceptor

    #
    # Generate the search screen
    #
    def generate( self ):
        return Content( [ centerAlign( self.line1 ),
                          centerAlign( self.line2 ) ] )

    def digit1( self ):
        return self.accept()

    def digit3( self ):
        return DisplayGenerator.left( self )

    def accept( self ):
        if self.acceptor:
            return self.acceptor()
        raise NotImplementedError, 'accept'

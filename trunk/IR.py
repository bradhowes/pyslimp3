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

import JVCRemote

class IR( object ):

    remotes = ( JVCRemote, )

    def __init__( self ):
        self.remoteMaps = {}
        for each in self.remotes:
            self.addRemote( each.remoteId, each.mapping )

    def addRemote( self, remoteId, mapping ):
        self.remoteMaps[ remoteId ] = mapping

    def lookup( self, remoteId, code ):
        return self.remoteMaps[ remoteId ].get( code )

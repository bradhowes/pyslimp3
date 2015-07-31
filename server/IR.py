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

#
# Container class that holds maps remote control IDs to remote control key code
# maps. Currently, only one remote control device is defined: JVC. To add a new
# remote control definition, first import it above, and then add the module to
# the list of remotes below.
#
class IR( object ):

    #
    # List of supported remote controllers
    #
    remotes = ( JVCRemote, )

    #
    # Constructor. Visit each remote control definition and add to the lookup
    # table remoteMaps.
    #
    def __init__( self ):
        self.remoteMaps = {}
        for each in self.remotes:
            self.remoteMaps[ each.remoteId ] = each.mapping

    #
    # Obtain a KeyProcessor key code for a given remote controller ID and
    # button code.
    #
    def lookup( self, remoteId, code ):
        return self.remoteMaps[ remoteId ].get( code )

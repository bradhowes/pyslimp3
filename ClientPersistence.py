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

import cPickle
from datetime import datetime
import Client

class ClientPersistence( object ):

    def __init__( self ):
        self.path = 'pyslimp3.pkl'
        self.clients = {}
        self.restore()

    def save( self ):
        cPickle.dump( self.clients, open( self.path, 'wb' ) )

    def restore( self ):
        try:
            self.clients = cPickle.load( open( self.path ) )
        except IOError:
            pass

    def getClient( self, server, addr ):
        key = repr( addr )
        client = self.clients.get( key, None )
        if client is None:
            client = Client.Client()
            self.clients[ key ] = client
        if not client.server:
            client.initialize( server, key )
        return client

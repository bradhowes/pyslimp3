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
        self.settings = {}
        self.restore()

    def save( self ):
        now = datetime.now()
        changed = False
        stale = []
        
        #
        # Visit all of the clients looking for changed state or staleness
        #
        for key, client in self.clients.items():
            state = client.getState()
            prev = self.settings.get( key[ 0 ], None )
            if prev is None:
                self.settings[ key[ 0 ] ] = state
                changed = True
            elif prev != state:
                prev.update( state )
                changed = True
            elif client.isStale( now ):
                print( '*** detected stale client', key )
                stale.append( key )

        for key in stale:
            client = self.clients[ key ]
            client.close()
            del self.clients[ key ]

        if changed:
            print( '... saving updated Client settings' )
            cPickle.dump( self.settings, open( self.path, 'wb' ) )

    def restore( self ):
        try:
            self.settings = cPickle.load( open( self.path ) )
            print( '... restored', len( self.settings ), 'settings:',
                   self.settings.keys() )
        except IOError:
            pass

    def getClient( self, server, addr ):
        client = self.clients.get( addr, None )
        if client is None:
            state = self.settings.get( addr[ 0 ], None )
            client = Client.Client( server, addr, state )
            self.clients[ addr ] = client
        return client

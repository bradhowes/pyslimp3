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
import Settings

#
# Maintainer of client settings. Uses Python's cPickle module to save/restore
# setting dictionaries for Client objects. Writes to disk when a setting
# changes.
#
class ClientPersistence( object ):

    def __init__( self, path = 'pyslimp3.pkl' ):
        self.path = path        # Location of the pickle file to use
        self.clients = {}       # Mapping of active Client objects
        self.settings = {}      # Mapping of available Settings objects
        self.restore()

    #
    # If any Client settings have changed, write the entire collection to disk.
    # Also, detect any Client objects that have not received any heartbeats
    # since some amount of time and cull them.
    #
    def save( self ):
        now = datetime.now()
        changed = False
        stale = []

        #
        # Visit all of the clients looking for changed state or staleness
        #
        for key, client in self.clients.items():
            if client.settingsAreDirty():
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

    #
    # Read the last saved collection of Settings objects.
    #
    def restore( self ):
        try:
            self.settings = cPickle.load( open( self.path ) )
            print( '... restored', len( self.settings ), 'settings:',
                   self.settings.keys() )
        except IOError:
            pass

    #
    # For a given host/port IP address pair, locate a Client object. If none
    # found, create a new one.
    #
    def getClient( self, server, addr ):
        key = addr[ 0 ]
        client = self.clients.get( key, None )
        if client is None:

            #
            # Get the settings object last seen for this address. If not found,
            # create a new one with default values.
            #
            settings = self.settings.get( key, None )
            if settings is None:
                settings = Settings.Settings()
                self.settings[ key ] = settings

            #
            # Create new Client object for the address.
            #
            print( 'getClient:', addr )
            client = Client.Client( server, addr, settings )
            self.clients[ key ] = client
        else:
            client.setHardwareAddress( addr )
        return client

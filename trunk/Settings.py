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

from datetime import datetime
from VFD import VFD

#
# Container of setting values for a Client object. There is a one-to-one
# relationship between a Settings object and a Client object. The Pyslimp3
# server periodically saves the contents of all Settings objects to disk so
# that when it restarts, future Client objects will have the same settings as
# they did prior to the restart.
#
class Settings( object ):

    #
    # Default values for new Client objects. Add new key definitions here,
    # along with their default value.
    #
    kDefaults = { 'brightness': VFD.kMaxBrightness,
                  'isOn': False,
                  'playbackFormatterIndex': 0,
                  'playlistForManipulation': '',
                  }

    def __init__( self ):
        
        #
        # All Client objects start out with the same default values.
        #
        self.dict = Settings.kDefaults.copy()
        self.dirty = False

    #
    # Obtain the value to pickle for this object. Returns the internal
    # dictionary.
    #
    def __getstate__( self ): 
        self.dirty = False
        return self.dict

    #
    # Install the pickled dictionary, thus restoring this object to a state it
    # was in in a past lifetime.
    #
    def __setstate__( self, value ): 
        self.dirty = False
        self.dict = value

        #
        # Bring the restored setting dictionary up-to-date by applying unknown
        # setting defaults.
        #
        for key, value in Settings.kDefaults.items():
            if not self.dict.has_key( key ):
                self.setValue( key, value )

    #
    # Obtain the current value for a given key.
    #
    def getValue( self, key ): return self.dict[ key ]

    #
    # Change the value for a given key, flagging this object as being dirty.
    #
    def setValue( self, key, value ): 
        old = self.dict.get( key, None )
        self.dict[ key ] = value
        self.dirty = True

    def isDirty( self ): return self.dirty

#
# Visit each of the keys defined in the Settings.kDefaults map, and create a
# getter and setter method for them.
#
for key in Settings.kDefaults:
    name = key[ 0 ].upper() + key[ 1 : ]
    def setter( s, v, k = key ):
        s.setValue( k, v )
    def getter( s, k = key ):
        return s.getValue( k )
    setattr( Settings, 'set' + name, setter )
    setattr( Settings, 'get' + name, getter )

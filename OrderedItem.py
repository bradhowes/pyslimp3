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

import VFD
import re

#
# Base class for names of albums and artists. Provides for a sane ordering that
# disregards capitalization, leading articles, and non-alphanumeric characters.
#
class OrderedItem( object ):

    __slots__ = ( 'name', 'key' )

    #
    # Set of text substitutions to apply to the name of the item.
    #
    kSubstitutions = ( 
        ( re.compile( ' & ' ), ' and ' ), # Spell out the '&' character
        ( re.compile( ' *\\.\\.\\. *' ),  # Shorten '...' to one character
          unichr( VFD.CustomCharacters.kEllipsis ) ),
        )

    def __init__( self, name ):

        #
        # Detect if we've been given another OrdererdItem for the name. Just
        # copy over its data
        #
        if isinstance( name, OrderedItem ):
            self.name = name.name
            self.key = name.key
            return

        #
        # Apply the text substitutions.
        #
        for pair in self.kSubstitutions:
            name = pair[ 0 ].sub( pair[ 1 ], name )

        self.name = name

        #
        # Generate the key value by making all words lower-case, removing
        # English and Spanish articles from the start of the name, and removing
        # any non-alphanumeric characters.
        #
        bits = name.upper().split()
        if bits[ 0 ] in ( 'A', 'AN', 'THE', 'EL', 'LA', 'LOS', 'LAS' ):
            bits = bits[ 1: ]

        self.key = filter( lambda a: a.isalnum() or a.isspace(), 
                           ' '.join( bits ) )

    def getName( self ): return self.name
    def getKey( self ): return self.key

    #
    # Obtain the hash value for this object. Uses the hash of the key
    #
    def __hash__( self ): return hash( self.key )

    #
    # Ordering definitions that rely on the key value
    #
    def __eq__( self, other ): return self.key == other.key
    def __ne__( self, other ): return self.key != other.key
    def __lt__( self, other ): return self.key < other.key
    def __le__( self, other ): return self.key <= other.key
    def __gt__( self, other ): return self.key > other.key
    def __ge__( self, other ): return self.key >= other.key

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

from Content import Content
from Display import *
from KeyProcessor import *

class RatingDisplay( iTunesSourceGenerator ):

    def __init__( self, source, prevLevel, obj ):
        iTunesSourceGenerator.__init__( self, source )
        self.prevLevel = prevLevel
        self.obj = obj

    def isOverlay( self ): return True

    def fillKeyMap( self ):
        iTunesSourceGenerator.fillKeyMap( self )
        self.addKeyMapEntry( kArrowLeft, ( kModFirst, ), self.left )
        self.addKeyMapEntry( kArrowUp, ( kModFirst, kModRepeat ), self.up )
        self.addKeyMapEntry( kArrowDown, ( kModFirst, kModRepeat ), self.down )

    def left( self ):
        return self.prevLevel

    def up( self ):
        self.setRating( self.obj, min( self.rating + 10, 100 ) )
        return self

    def down( self ):
        self.setRating( self.obj, max( self.rating - 10, 0 ) )
        return self

    def generate( self ):
        self.rating = rating = self.getRating( self.obj )
        numStars = rating // 20
        halfStar = ( rating - numStars * 20 ) // 10
        stars = '*' * numStars
        if halfStar:
            stars += ' 1/2'
        return Content( [ self.obj.getName(),
                          centerAlign( stars ) ],
                        [ 'Rating', 
                          '' ] )

class AlbumRatingDisplay( RatingDisplay ):

    def __init__( self, source, prevLevel, album ):
        RatingDisplay.__init__( self, source, prevLevel, album )
    def getRating( self, obj ): 
        return self.source.getAlbumRating( obj )
    def setRating( self, obj, value ): 
        self.source.setAlbumRating( obj, value )

class TrackRatingDisplay( RatingDisplay ):

    def __init__( self, source, prevLevel, track ):
        RatingDisplay.__init__( self, source, prevLevel, track )
    def getRating( self, obj ): 
        return self.source.getTrackRating( obj )
    def setRating( self, obj, value ): 
        self.source.setTrackRating( obj, value )

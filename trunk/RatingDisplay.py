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

#
# Temporary (overlay) display of the current user rating for a song or album.
# Use the up/down arrow buttons to change the rating.
#
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
        self.setRating( min( self.getRating() + 10, 100 ) )
        return self

    def down( self ):
        self.setRating( max( self.getRating() - 10, 0 ) )
        return self

    def generate( self ):
        rating = self.getRating()
        numStars = rating // 20
        halfStar = ( rating - numStars * 20 ) // 10
        stars = '%d' % numStars
        stars = '*' * numStars
        if halfStar:
            stars += ' 1/2'
        return Content( [ self.obj.getName(),
                          centerAlign( stars + ' stars' ) ],
                        [ 'Rating', 
                          '' ] )

    #
    # Override of DisplayGenerator method. Convert digits 0-5 into a rating
    # from 0-100. Anything larger
    #
    def digit( self, digit ):
        if digit > 5:
            digit = 5
        rating = digit * 20
        self.setRating( rating )
        return self
#
# Derviation of RatingDisplay that works with albums.
#
class AlbumRatingDisplay( RatingDisplay ):
    def __init__( self, source, prevLevel, album ):
        RatingDisplay.__init__( self, source, prevLevel, album )
    def getRating( self ): 
        return self.source.getAlbumRating( self.obj )
    def setRating( self, value ): 
        self.source.setAlbumRating( self.obj, value )

#
# Derviation of RatingDisplay that works with artists.
#
class TrackRatingDisplay( RatingDisplay ):
    def __init__( self, source, prevLevel, track ):
        RatingDisplay.__init__( self, source, prevLevel, track )
    def getRating( self ): 
        return self.source.getTrackRating( self.obj )
    def setRating( self, value ): 
        self.source.setTrackRating( self.obj, value )

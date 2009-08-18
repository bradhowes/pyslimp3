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
from VFD import CustomCharacters

#
# Temporary (overlay) display of the current user rating for a song or album.
# Use the up/down arrow buttons to change the rating. Also supports using the
# keys 0-5 to directly set the rating. With the arrow keys, one can set
# half-stars.
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

    def setRating( self, value ):
        raise NotImplementedError, 'RatingDisplay.setRating'

    def up( self ):
        value = min( self.getRating() + 10, 100 )
        self.setRating( value )
        return self

    def down( self ):
        value = max( self.getRating() - 10, 0 )
        self.setRating( value )
        return self

    def generateRatingIndicator( self, rating ):
        fullStars = rating / 20
        halfStar = rating - fullStars * 20
        indicator = u'%d.%d ' % ( fullStars, halfStar / 2, )
        indicator += unichr( CustomCharacters.kRatingFilled ) * fullStars
        emptyStars = 5 - fullStars
        if halfStar:
            indicator += unichr( CustomCharacters.kRatingHalf )
            emptyStars -= 1
        if emptyStars > 0:
            indicator += unichr( CustomCharacters.kRatingEmpty ) * emptyStars
        return indicator

    #
    # Override of DisplayGenerator method. Convert digits 0-5 into a rating
    # from 0-100. Does not support half-stars.
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
    def fillKeyMap( self ):
        RatingDisplay.fillKeyMap( self )
        self.addKeyMapEntry( kPIP, ( kModFirst, ), self.left )
    def getRating( self ): 
        return self.source.getAlbumRating( self.obj )
    def setRating( self, value ): 
        self.source.setAlbumRating( self.obj, value )
    def generate( self ):
        indicator = self.generateRatingIndicator( self.getRating() )
        return Content( [ self.obj.getName(),
                          centerAlign( indicator ) ],
                        [ 'Album Rating', 
                          '' ] )

#
# Derviation of RatingDisplay that works with tracks.
#
class TrackRatingDisplay( RatingDisplay ):
    def __init__( self, source, prevLevel, track ):
        RatingDisplay.__init__( self, source, prevLevel, track )
    def fillKeyMap( self ):
        RatingDisplay.fillKeyMap( self )
        self.addKeyMapEntry( kPIP, ( kModFirst, ), self.albumRating )
    def albumRating( self ):
        album = self.source.getAlbum( self.obj.getAlbumName() )
        return AlbumRatingDisplay( self.source, self, album )
    def getRating( self ): 
        return self.source.getTrackRating( self.obj )[ 0 ]
    def setRating( self, value ): 
        self.source.setTrackRating( self.obj, value )
    def generate( self ):
        trackRating, albumRating = self.source.getTrackRating( self.obj )
        trackIndicator = self.generateRatingIndicator( trackRating )
        albumIndicator = self.generateRatingIndicator( albumRating )
        line2 = 'Track: ' + trackIndicator + ' - Album: ' + albumIndicator
        return Content( [ self.obj.getName(),
                          centerAlign( line2 ) ],
                        [ 'Track Rating', 
                          '' ] )

//
// (C) Copyright 2009 Brad Howes. All rights reserved.
//
// This file is part of Pyslimp3.
//
// Pyslimp3 is free software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the Free Software
// Foundation; either version 3, or (at your option) any later version.
//
// Pyslimp3 is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
// A PARTICULAR PURPOSE. See the GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along with
// Pyslimp3; see the file COPYING. If not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
// USA.
//

#include <iostream>

#include "VFDElementData.h"

VFDElementData::VFDElementData()
    : data_( 0, kRows ), bits_()
{
    init();
}

VFDElementData::VFDElementData( const RawDef& data )
    : data_( data, data + kRows ), bits_()
{
    init();
}

void
VFDElementData::setBits( const RawDef& data )
{
    std::copy( data, data + kRows, data_.begin() );
    emit changed();
}

void
VFDElementData::setBits( const std::vector<int>& data )
{
    data_ = data;
    emit changed();
}

bool
VFDElementData::isSet( int row, int column ) const
{
    return data_[ row ] & bits_[ column ];
}

void
VFDElementData::init()
{
    int bit = 1 << ( kColumns - 1 );
    for ( int index = 0; index < kColumns; ++index ) {
	bits_.push_back( bit );
	bit >>= 1;
    }
}

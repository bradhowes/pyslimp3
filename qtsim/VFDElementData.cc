//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
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

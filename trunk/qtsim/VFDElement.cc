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

#include <QtGui/QPainter>

#include "VFDElement.h"
#include "VFDElementData.h"

VFDElement::VFDElement( QWidget* parent )
    : Super( parent ), onColor_( Qt::green ), offColor_( Qt::black ),
      backgroundColor_( Qt::black ), pixelSize_( 3 ), spacing_( 1 ),
      data_( 0 )
{
    adjustedOnColor_ = onColor_;
    setSizePolicy( QSizePolicy( QSizePolicy::Fixed, QSizePolicy::Fixed ) );
}

QSize
VFDElement::getSize() const
{
    return QSize( VFDElementData::kColumns * pixelSize_ +
		  ( VFDElementData::kColumns - 1 ) * spacing_,
		  VFDElementData::kRows * pixelSize_ +
		  ( VFDElementData::kRows - 1 ) * spacing_ );
}

void
VFDElement::setOnColor( QColor color )
{
    onColor_ = color;
    update();
}

void
VFDElement::setOffColor( QColor color )
{
    offColor_ = color;
    update();
}

void
VFDElement::setBackgroundColor( QColor color )
{
    backgroundColor_ = color;
    update();
}

void
VFDElement::setPixelSize( int value )
{
    if ( value < 1 ) value = 1;
    if ( value == pixelSize_ ) return;
    pixelSize_ = value;
    adjustSize();
    update();
}

void
VFDElement::setSpacing( int value )
{
    if ( value < 0 ) value = 0;
    if ( value == spacing_ ) return;
    spacing_ = value;
    adjustSize();
    update();
}

void
VFDElement::setBrightness( int brightness )
{
    brightness_ = brightness;
}

void
VFDElement::setData( VFDElementData* data )
{
    setData( data, brightness_ );
}

void
VFDElement::setData( VFDElementData* data, int brightness )
{
    brightness_ = brightness;
    if ( data_ ) data_->disconnect( this );
    data_ = data;
    if ( data_ ) connect( data_, SIGNAL( changed() ), SLOT( update() ) );
    adjustedOnColor_ = onColor_;
    if ( brightness == 0 )
	adjustedOnColor_ = onColor_;
    else
	adjustedOnColor_ = onColor_.darker( 75 * brightness + 100 );
    update();
}

void
VFDElement::paintEvent( QPaintEvent* )
{
    QPainter painter( this );
    painter.fillRect( rect(), QBrush( backgroundColor_ ) );
    QRectF rect( 0, 0, pixelSize_, pixelSize_ );

    for ( int row = 0; row < VFDElementData::kRows; ++row ) {
	for ( int col = 0; col < VFDElementData::kColumns; ++col ) {
	    rect.moveTo( col * ( pixelSize_ + spacing_ ),
			 row * ( pixelSize_ + spacing_ ) );
	    if ( data_ && data_->isSet( row, col ) )
		painter.fillRect( rect, adjustedOnColor_ );
	    else
		painter.fillRect( rect, offColor_ );
	}
    }
}

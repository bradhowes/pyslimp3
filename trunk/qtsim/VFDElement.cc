//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

#include <iostream>

#include <QtGui/QPainter>

#include "VFDElement.h"
#include "VFDElementData.h"

VFDElement::VFDElement( QWidget* parent )
    : Super( parent ), onColor_( Qt::green ), offColor_( Qt::black ),
      backgroundColor_( Qt::black ), pixelSize_( 4 ), spacing_( 1 ),
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
VFDElement::setData( VFDElementData* data, int brightness )
{
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

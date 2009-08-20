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

#include <arpa/inet.h>
#include <iomanip>
#include <iostream>

#include <QtCore/QTimer>
#include <QtGui/QHBoxLayout>
#include <QtNetwork/QUdpSocket>

#include "MainWindow.h"
#include "Remote.h"
#include "VFDElement.h"
#include "VFDElementData.h"

static const VFDElementData::RawDef definitions[] = {
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x00
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x01
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x02
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x03
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x04
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x05
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x06
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x07
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x08
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x09
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x0A
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x0B
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x0C
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x0D
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x0E
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x0F
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x10
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x11
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x12
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x13
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x14
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x15
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x16
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x17
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x18
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x19
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x1A
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x1B
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x1C
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x1D
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x1E
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x1F
    { 0, 0, 0, 0, 0, 0, 0, 0 },	       // 0x20 <space>
    { 4, 4, 4, 4, 0, 0, 4, 0 },	       // 0x21 !
    { 10, 10, 10, 0, 0, 0, 0, 0 },     // 0x22 "
    { 10, 10, 31, 10, 31, 10, 10, 0 }, // 0x23 #
    { 4, 15, 20, 14, 1, 30, 4, 0 },    // 0x24 $
    { 24, 25, 2, 4, 8, 19, 3, 0 },     // 0x25 %
    { 12, 18, 20, 8, 21, 18, 13, 0 },  // 0x26 &
    { 12, 4, 8, 0, 0, 0, 0, 0 },       // 0x27 '
    { 2, 4, 8, 8, 8, 4, 2, 0 },	       // 0x28 (
    { 8, 4, 2, 2, 2, 4, 8, 0 },	       // 0x29 )
    { 0, 4, 21, 14, 21, 4, 0, 0 },     // 0x2A *
    { 0, 4, 4, 31, 4, 4, 0, 0 },       // 0x2B +
    { 0, 0, 0, 0, 12, 4, 8, 0 },       // 0x2C ,
    { 0, 0, 0, 31, 0, 0, 0, 0 },       // 0x2D -
    { 0, 0, 0, 0, 0, 12, 12, 0 },      // 0x2E .
    { 0, 1, 2, 4, 8, 16, 0, 0 },       // 0x2F /
    { 14, 17, 19, 21, 25, 17, 14, 0 }, // 0x30 0
    { 4, 12,  4,  4,  4,  4, 14, 0 },  // 0x31 1
    { 14, 17,  1,  2,  4,  8, 31, 0 }, // 0x32 2
    { 31,  2,  4,  2,  1, 17, 14, 0 }, // 0x33 3
    { 2, 6, 10, 18, 31, 2, 2, 0 },     // 0x34 4
    { 31, 16, 30, 1, 1, 17, 14, 0 },   // 0x35 5
    { 6, 8, 16, 30, 17, 17, 14, 0 },   // 0x36 6
    { 31, 1, 2, 4, 8, 8, 8, 0 },       // 0x37 7
    { 14, 17, 17, 14, 17, 17, 14, 0 }, // 0x38 8
    { 14, 17, 17, 15, 1, 2, 12, 0 },   // 0x39 9
    { 0, 12, 12, 0, 12, 12, 0, 0 },    // 0x3A :
    { 0, 12, 12, 0, 12, 4, 8, 0 },     // 0x3B ;
    { 2, 4, 8, 16, 8, 4, 2, 0 },       // 0x3C <
    { 0, 0, 31, 0, 31, 0, 0, 0 },      // 0x3D =
    { 8, 4, 2, 1, 2, 4, 8, 0 },	       // 0x3E >
    { 14, 17, 1, 2, 4, 0, 4, 0 },      // 0x3F ?
    { 14, 17, 1, 13, 21, 21, 14, 0 },  // 0x40 @
    { 14, 17, 17, 17, 31, 17, 17, 0 }, // 0x41 A
    { 30, 17, 17, 30, 17, 17, 30, 0 }, // 0x42 B
    { 14, 17, 16, 16, 16, 17, 14, 0 }, // 0x43 C
    { 28, 18, 17, 17, 17, 18, 28, 0 }, // 0x44 D
    { 31, 16, 16, 30, 16, 16, 31, 0 }, // 0x45 E
    { 31, 16, 16, 30, 16, 16, 16, 0 }, // 0x46 F
    { 14, 17, 16, 23, 17, 17, 15, 0 }, // 0x47 G
    { 17, 17, 17, 31, 17, 17, 17, 0 }, // 0x48 H
    { 14, 4, 4, 4, 4, 4, 14, 0 },      // 0x49 I
    { 7, 2, 2, 2, 2, 18, 14, 0 },      // 0x4A J
    { 17, 18, 20, 24, 20, 18, 17, 0 }, // 0x4B K
    { 16, 16, 16, 16, 16, 16, 31, 0 }, // 0x4C L
    { 17, 27, 21, 21, 17, 17, 17, 0 }, // 0x4D M
    { 17, 17, 25, 21, 19, 17, 17, 0 }, // 0x4E N
    { 14, 17, 17, 17, 17, 17, 14, 0 }, // 0x4F O
    { 30, 17, 17, 30, 16, 16, 16, 0 }, // 0x50 P
    { 14, 17, 17, 17, 21, 18, 13, 0 }, // 0x51 Q
    { 30, 17, 17, 30, 20, 18, 17, 0 }, // 0x52 R
    { 15, 16, 16, 14, 1, 1, 30, 0 },   // 0x53 S
    { 31, 4, 4, 4, 4, 4, 4, 0 },       // 0x54 T
    { 17, 17, 17, 17, 17, 17, 14, 0 }, // 0x55 U
    { 17, 17, 17, 17, 17, 10, 4, 0 },  // 0x56 V
    { 17, 17, 17, 21, 21, 21, 10, 0 }, // 0x57 W
    { 17, 17, 10, 4, 10, 17, 17, 0 },  // 0x58 X
    { 17, 17, 17, 10, 4, 4, 4, 0 },    // 0x59 Y
    { 31, 1, 2, 4, 8, 16, 31, 0 },     // 0x5A Z
    { 14, 8, 8, 8, 8, 8, 14, 0 },      // 0x5B [
    { 0, 16, 8, 4, 2, 1, 0, 0 },       // 0x5C <backslash>
    { 14, 2, 2, 2, 2, 2, 14, 0 },      // 0x5D ]
    { 4, 10, 17, 0, 0, 0, 0, 0 },      // 0x5E ^
    { 0, 0, 0, 0, 0, 0, 31, 0 },       // 0x5F _
    { 8, 4, 2, 0, 0, 0, 0, 0 },	       // 0x60 `
    { 0, 0, 14, 1, 15, 17, 15, 0 },    // 0x61 a
    { 16, 16, 22, 25, 17, 17, 30, 0 }, // 0x62 b
    { 0, 0, 14, 16, 16, 17, 14, 0 },   // 0x63 c
    { 1, 1, 13, 19, 17, 17, 15, 0 },   // 0x64 d
    { 0, 0, 14, 17, 31, 16, 14, 0 },   // 0x65 e
    { 6, 9, 8, 28, 8, 8, 8, 0 },       // 0x66 f
    { 0, 15, 17, 17, 15, 1, 14, 0 },   // 0x67 g
    { 16, 16, 22, 25, 17, 17, 17, 0 }, // 0x68 h
    { 4, 0, 12, 4, 4, 4, 14, 0 },      // 0x69 i
    { 2, 0, 6, 2, 2, 18, 12, 0 },      // 0x6A j
    { 16, 16, 18, 20, 24, 20, 18, 0 }, // 0x6B k
    { 12, 4, 4, 4, 4, 4, 14, 0 },      // 0x6C l
    { 0, 0, 26, 21, 21, 17, 17, 0 },   // 0x6D m
    { 0, 0, 22, 25, 17, 17, 17, 0 },   // 0x6E n
    { 0, 0, 14, 17, 17, 17, 14, 0 },   // 0x6F o
    { 0, 0, 30, 17, 30, 16, 16, 0 },   // 0x70 p
    { 0, 0, 13, 19, 15, 1, 1, 0 },     // 0x71 q
    { 0, 0, 22, 25, 16, 16, 16, 0, },  // 0x72 r
    { 0, 0, 14, 16, 14, 1, 30, 0, },   // 0x73 s
    { 8, 8, 28, 8, 8, 9, 6, 0, },      // 0x74 t
    { 0, 0, 17, 17, 17, 19, 13, 0, },  // 0x75 u
    { 0, 0, 17, 17, 17, 10, 4, 0, },   // 0x76 v
    { 0, 0, 17, 17, 21, 21, 10, 0 },   // 0x77 w
    { 0, 0, 17, 10, 4, 10, 17, 0 },    // 0x78 x
    { 0, 0, 17, 17, 15, 1, 14, 0 },    // 0x79 y
    { 0, 0, 31, 2, 4, 8, 31, 0 },      // 0x7A x
    { 2, 4, 4, 8, 4, 4, 2, 0 },	       // 0x7B {
    { 4, 4, 4, 4, 4, 4, 4, 0 },	       // 0x7C |
    { 8, 4, 4, 2, 4, 4, 8, 0 },	       // 0x7D }
    { 0, 0, 4, 2, 31, 2, 4, 0 },       // 0x7E <right arrow>
    { 0, 0, 4, 8, 31, 8, 4, 0 },       // 0x7F <left arrow>
    { 31, 31, 31, 31, 31, 31, 31, 0 }, // 0x80 <block>
};

MainWindow::MainWindow()
    : QWidget(), timeSource_(), remote_( new Remote ), bits_(), elements_(),
      timer_( new QTimer( this ) ),
      serverSocket_( new QUdpSocket( this ) ),
      serverAddress_( QHostAddress::Broadcast ),
      lastTimeStamp_( QDateTime::currentDateTime() )
{
    timeSource_.start();

    QPalette p( palette() );
    p.setColor( QPalette::Background, Qt::black );
    p.setColor( QPalette::Window, Qt::black );
    setPalette( p );
    setAutoFillBackground( true );

    const VFDElementData::RawDef* ptr = definitions;
    while( bits_.size() <= 128 ) {
	VFDElementData* data = new VFDElementData( *ptr++ );
	bits_.push_back( data );
    }

    QVBoxLayout* rows = new QVBoxLayout;
    rows->setContentsMargins( 40, 40, 40, 40 );
    rows->setSizeConstraint( QLayout::SetFixedSize );
    rows->setSpacing( 4 );

    QHBoxLayout* row1 = new QHBoxLayout;
    row1->setContentsMargins( 0, 0, 0, 0 );
    row1->setSizeConstraint( QLayout::SetFixedSize );
    row1->setSpacing( 4 );
    for ( int index = 0; index < 40; ++index ) {
	VFDElement* w = new VFDElement( this );
	w->setData( bits_[ 32 ] );
	row1->addWidget( w );
	elements_.push_back( w );
    }

    QHBoxLayout* row2 = new QHBoxLayout;
    row2->setContentsMargins( 0, 0, 0, 0 );
    row2->setSizeConstraint( QLayout::SetFixedSize );
    row2->setSpacing( 4 );
    for ( int index = 0; index < 40; ++index ) {
	VFDElement* w = new VFDElement( this );
	w->setData( bits_[ 32 ] );
	row2->addWidget( w );
	elements_.push_back( w );
    }

    rows->addLayout( row1 );
    rows->addLayout( row2 );

    setLayout( rows );

    connect( remote_, SIGNAL( keyPressed( uint32_t ) ),
	     SLOT( sendKey( uint32_t ) ) );
    remote_->show();
    remote_->raise();
    remote_->activateWindow();

    if ( ! serverSocket_->bind() )
	std::clog << "*** failed to bind\n";
    
    connect( serverSocket_, SIGNAL( readyRead() ), SLOT( readMessage() ) );

    timer_->start( 5000 );
    connect( timer_, SIGNAL( timeout() ), SLOT( emitHeartbeat() ) );

    emitDiscovery();
}

void
MainWindow::mousePressEvent( QMouseEvent* )
{
    remote_->show();
    remote_->raise();
}

void
MainWindow::sendKey( uint32_t keyCode )
{
    int msecs = timeSource_.elapsed();
    sendKeyMessage( msecs, keyCode );
}

void
MainWindow::sendKeyMessage( uint32_t when, uint32_t keyCode )
{
    buffer_[ 0 ] = 'i';
    buffer_[ 1 ] = 0;
    writeInteger( htonl( when ), 2 );
    buffer_[ 6 ] = 0;
    buffer_[ 7 ] = 0;
    writeInteger( htonl( keyCode ), 8 );
    writeMessage( 18 );
}

void
MainWindow::writeInteger( uint32_t value, size_t offset )
{
    value = htonl( value );
    buffer_[ offset++ ] = ( value >> 24 ) & 0xFF;
    buffer_[ offset++ ] = ( value >> 16 ) & 0xFF;
    buffer_[ offset++ ] = ( value >>  8 ) & 0xFF;
    buffer_[ offset++ ] = ( value >>  0 ) & 0xFF;
}

void
MainWindow::emitHeartbeat()
{
    if ( serverAddress_ != QHostAddress::Broadcast ) {
	QDateTime now( QDateTime::currentDateTime() );
	if ( lastTimeStamp_.secsTo( now ) > 30 ) {
	    std::clog << "*** detected stale server\n";
	    serverAddress_ = QHostAddress::Broadcast;
	    lastTimeStamp_ = now;
	}
	else {
	    emitHello();
	    return;
	}
    }

    emitDiscovery();
}

void
MainWindow::emitDiscovery()
{
    setDisplay( "Looking for server...", "" );
    buffer_[ 0 ] = 'd';
    for ( int index = 1; index < 18; ++index ) buffer_[ index ] = 0;
    writeMessage( 18 );
}

void
MainWindow::emitHello()
{
    buffer_[ 0 ] = 'h';
    for ( int index = 1; index < 18; ++index ) buffer_[ index ] = 0;
    writeMessage( 18 );
}

void
MainWindow::readMessage()
{
    while ( serverSocket_->hasPendingDatagrams() ) {
	qint64 size = serverSocket_->readDatagram( (char*)buffer_, 4096,
						   &serverAddress_ );
	bufferSize_ = size;
	// std::clog << "bufferSize: " << bufferSize_ << std::endl;
	if ( size > 0 ) {
	    lastTimeStamp_ = QDateTime::currentDateTime();
	    switch ( buffer_[ 0 ] ) {
	    case 'D':
		std::clog << "server host: "
			  << serverAddress_.toString().toStdString()
			  << std::endl;
		emitHello();
		break;

	    case 'l':
		// dumpBuffer();
		updateDisplay();
		break;
	    }
	}
	else {
	    std::clog << "*** readDatagram returned " << size
		      << std::endl;
	}
    }
}

void
MainWindow::dumpBuffer()
{
    size_t index = 0;
    std::clog << std::hex;
    while ( index < bufferSize_ ) {
	std::clog << std::setw( 2 ) << int( buffer_[ index++ ] ) << ' ';
	if ( ( index % 16 ) == 0 ) std::clog << '\n';
    }

    std::clog << std::dec;
    if ( ( index % 16 ) > 0 ) std::clog << '\n';
}

void
MainWindow::updateDisplay()
{
    // std::clog << "updateDisplay\n";
    size_t index = 18;
    while ( index < bufferSize_ ) {
	index = processEntry( index );
    }
}

size_t
MainWindow::processEntry( size_t index )
{
    if ( index + 1 < bufferSize_ ) {
	// std::clog << "processEntry: " << int( buffer_[ index ] ) << std::endl;
	switch ( buffer_[ index ] ) {
	case 0x02: return processCommand( index + 1 ); break;
	case 0x03: return processCharacter( index + 1 ); break;
	default: std::clog << "*** unknown prefix - " << int( buffer_[ index ] )
			   << "\n"; break;
	};
    }
    return bufferSize_;
}

size_t
MainWindow::processCharacter( size_t index )
{
    int c = buffer_[ index++ ];
    if ( c >= bits_.size() ) c = 32;
    if ( elementIndex_ < elements_.size() ) {
	// std::clog << "processCharacter: " << c << ' ' << elementIndex_
	// << std::endl;
	elements_[ elementIndex_++ ]->setData( bits_[ c ] );
    }
    return index;
}

size_t
MainWindow::processCommand( size_t index )
{
    // std::clog << "processCommand: " << int( buffer_[ index ] ) << std::endl;
    switch ( buffer_[ index ] ) {
    case 0x33: clearDisplay(); return index + 1;
    case 0x30: return processBrightness( index + 1 );
    case 0x06: return index + 1;
    case 0x02: elementIndex_ = 0; return index + 1;
    case 0xC0: elementIndex_ = 40; return index + 1;
    case 0x0C: return index + 1;
    default: break;
    }

    if ( buffer_[ index ] & 0x40 ) 
	return processCustomDefinition( index );

    return index + 1;
}

size_t
MainWindow::processBrightness( size_t index )
{
    if ( index + 1 < bufferSize_ && buffer_[ index ] == 0x03 ) {
	int brightness = buffer_[ index + 1 ];
	// std::clog << "processBrightness: " << brightness << std::endl;
	for ( int z = 0; z < elements_.size(); ++z )
	    elements_[ z ]->setBrightness( brightness );
    }
    return index + 2;
}

size_t
MainWindow::processCustomDefinition( size_t index )
{
    //
    // Extract the custom character index (0-31)
    //
    uint32_t bitsIndex = buffer_[ index++ ];

    bitsIndex = ( bitsIndex - 0x40 ) / 8;
    // std::clog << "processCustomDefinition: " << bitsIndex << std::endl;

    std::vector<int> bits;

    //
    // Extract the bit settings
    //
    while ( index + 1 < bufferSize_ && buffer_[ index ] == 0x03 ) {
	bits.push_back( buffer_[ index + 1 ] );
	index += 2;
    }

    while ( bits.size() < 8 )
	bits.push_back( 0 );

    if ( bitsIndex < 32 )
	bits_[ bitsIndex ]->setBits( bits );

    return index;
}

void
MainWindow::clearDisplay()
{
    for ( int index = 0; index < elements_.size(); ++index ) {
	elements_[ index ]->setData( bits_[ 32 ] );
    }
}

void
MainWindow::setDisplay( const std::string& line1, const std::string& line2 )
{
    for ( size_t index = 0; index < line1.size() && index < 40; ++index ) {
	int c = line1[ index ];
	if ( c < 32 or c >= bits_.size() ) c = 32;
	elements_[ index ]->setData( bits_[ line1[ index ] ] );
    }

    for ( size_t index = 0; index < line2.size() && index < 40; ++index ) {
	int c = line1[ index ];
	if ( c < 32 or c >= bits_.size() ) c = 32;
	elements_[ index + 40 ]->setData( bits_[ line2[ index ] ] );
    }
}

void
MainWindow::writeMessage( size_t count )
{
    while ( 1 ) {

	qint64 size = serverSocket_->writeDatagram( (char*)buffer_, count,
						    serverAddress_, 3483 );
	if ( size == -1 ) {
	    std::clog << "*** failed writeDatagram\n";
	    if ( serverAddress_ == QHostAddress::Broadcast ) {
		serverAddress_ = QHostAddress::LocalHost;
		continue;
	    }
	    else if ( serverAddress_ != QHostAddress::LocalHost ) {
		serverAddress_ = QHostAddress::Broadcast;
		continue;
	    }
	}

	break;
    }
}

//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

#include <arpa/inet.h>
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
    : QWidget(), remote_( new Remote ), bits_(), row1_(), row2_(),
      timer_( new QTimer( this ) ), serverSocket_( new QUdpSocket( this ) ),
      foundServer_( false )
{
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

    std::cout << "bits_.size(): " << bits_.size() << std::endl;

    int bitIndex = 48;

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
	w->setData( bits_[ bitIndex++ ], index % 4 );
	row1->addWidget( w );
	row1_.push_back( w );
    }

    QHBoxLayout* row2 = new QHBoxLayout;
    row2->setContentsMargins( 0, 0, 0, 0 );
    row2->setSizeConstraint( QLayout::SetFixedSize );
    row2->setSpacing( 4 );
    for ( int index = 0; index < 40; ++index ) {
	VFDElement* w = new VFDElement( this );
	w->setData( bits_[ bitIndex++ ], index % 4 );
	row2->addWidget( w );
	row2_.push_back( w );
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
    static double kTicksPerSecond = 625000.0;
    // std::clog << "sendKey: " << keyCode << std::endl;
    sendKeyMessage( 0x000112233, keyCode );
    sendKeyMessage( int( ( 0x000112233 + 0.100 ) * kTicksPerSecond ),
		    keyCode );
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
    if ( foundServer_ ) {
	emitHello();
    }
    else {
	emitDiscovery();
    }
}

void
MainWindow::emitDiscovery()
{
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
	qint64 size = serverSocket_->readDatagram( buffer_, 2048 );
	// std::clog << "readMessage: " << size << std::endl;
	if ( size > 0 ) {
	    switch ( buffer_[ 0 ] ) {
	    case 'D': foundServer_ = true; emitHello(); break;
	    case 'l': updateDisplay(); break;
	    }
	}
    }
}

void
MainWindow::updateDisplay()
{
    int brightness = buffer_[ 25 ];
    std::clog << "brightness: " << int( buffer_[ 25 ] ) << ' ' << brightness
	      << std::endl;

    //
    // !!! FIXME: kinda hacky 
    //
    int bufferIndex = 26;	// Start of the character data.

    //
    // See if there are custom characters to load.
    //
    while ( buffer_[ bufferIndex + 1 ] != 0x06 ) {

	//
	// Extract the custom character index (0-31)
	//
	uint32_t bitsIndex = buffer_[ bufferIndex + 1 ];
	bitsIndex = ( bitsIndex - 0x40 ) / 8;

	//
	// Extract the bit settings
	//
	std::vector<int> bits;
	for ( int z = 0; z < 8; ++z )
	    bits.push_back( buffer_[ bufferIndex + 3 + z * 2 ] );

	//
	// Update the VFDElementData object that corresponds to the custom
	// index.
	//
	if ( bitsIndex < 32 )
	    bits_[ bitsIndex ]->setBits( bits );

	bufferIndex += 18;	// Move to next entry
    }

    bufferIndex += 4;		// Skip over the clear and home commands

    //
    // Assign the appropriate VFDElementData to each VFDElement in the first
    // line.
    //
    int elementIndex = 0;
    while ( buffer_[ bufferIndex ] == 0x03 ) { // character data
	unsigned int c = buffer_[ bufferIndex + 1 ];
	if ( c > 128 ) c = 128;
	row1_[ elementIndex++ ]->setData( bits_[ c ], brightness );
	bufferIndex += 2;
    }

    bufferIndex += 2;		// Skip over the next line command

    //
    // Assign the appropriate VFDElementData to each VFDElement in the second
    // line.
    //
    elementIndex = 0;
    while ( buffer_[ bufferIndex ] == 0x03 ) { // character data
	unsigned int c = buffer_[ bufferIndex + 1 ];
	if ( c > 128 ) c = 128;
	row2_[ elementIndex++ ]->setData( bits_[ c ], brightness );
	bufferIndex += 2;
    }
}

void
MainWindow::writeMessage( size_t count )
{
    qint64 size = serverSocket_->writeDatagram( buffer_, count,
						QHostAddress::LocalHost, 3483 );
    if ( size == -1 )
	std::clog << "*** failed writeDatagram\n";
}

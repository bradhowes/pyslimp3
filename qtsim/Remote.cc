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
#include <QtGui/QMouseEvent>

#include "MainWindow.h"
#include "Remote.h"

//
// Mapping of key name, Qt key code and remote keycode that an actual remote
// would emit.
//
struct KeyCodeMapEntry {
    KeyCodeMapEntry( const char* n, int c, int k )
	: name( n ), keyCode( c ), key( k ) {}
    QString name;		// Name of the button in the remote GUI
    uint32_t keyCode;		// Remote key code to send to Pyslimp3 server
    uint32_t key;		// Qt key code from user keyPress event
};

//
// Key definitions supported by the remote.
//
static const KeyCodeMapEntry inits[] = {
    KeyCodeMapEntry( "power", 0xf702, Qt::Key_Q ),
    KeyCodeMapEntry( "one", 0xf786, Qt::Key_1 ),
    KeyCodeMapEntry( "two", 0xf746, Qt::Key_2 ),
    KeyCodeMapEntry( "three", 0xf7c6, Qt::Key_3 ),
    KeyCodeMapEntry( "four", 0xf726, Qt::Key_4 ),
    KeyCodeMapEntry( "five", 0xf7a6, Qt::Key_5 ),
    KeyCodeMapEntry( "six", 0xf766, Qt::Key_6 ),
    KeyCodeMapEntry( "seven", 0xf7e6, Qt::Key_7 ),
    KeyCodeMapEntry( "eight", 0xf716, Qt::Key_8 ),
    KeyCodeMapEntry( "nine", 0xf796, Qt::Key_9 ),
    KeyCodeMapEntry( "zero", 0xf776, Qt::Key_0 ),
    KeyCodeMapEntry( "rewind", 0xf70e, Qt::Key_Less ),
    KeyCodeMapEntry( "play", 0xf732, Qt::Key_P ),
    KeyCodeMapEntry( "fastForward", 0xf76e, Qt::Key_Greater ),
    KeyCodeMapEntry( "pause", 0xf7b2, Qt::Key_Space ),
    KeyCodeMapEntry( "stop", 0xf7c2, Qt::Key_S ),
    KeyCodeMapEntry( "left", 0xf74b, Qt::Key_Left ),
    KeyCodeMapEntry( "right", 0xf7cb, Qt::Key_Right ),
    KeyCodeMapEntry( "up", 0xf70b, Qt::Key_Up ),
    KeyCodeMapEntry( "down", 0xf78b, Qt::Key_Down ),
    KeyCodeMapEntry( "volumeUp", 0xf778, Qt::Key_BracketRight ),
    KeyCodeMapEntry( "volumeDown", 0xf7f8, Qt::Key_BracketLeft ),
    KeyCodeMapEntry( "brightnessUp", 0xf70d, Qt::Key_BraceRight ),
    KeyCodeMapEntry( "brightnessDown", 0xf78d, Qt::Key_BraceLeft ),
    KeyCodeMapEntry( "disp", 0xf703, Qt::Key_D ),
    KeyCodeMapEntry( "guide", 0xf7b6, Qt::Key_G ),
    KeyCodeMapEntry( "menu", 0xf783, Qt::Key_M ),
    KeyCodeMapEntry( "pip", 0xf7f6, Qt::Key_I ),
    KeyCodeMapEntry( "rec", 0xf743, Qt::Key_R ),
    KeyCodeMapEntry( "recall", 0xf7ab, Qt::Key_A ),
    KeyCodeMapEntry( "sleep", 0xf7b3, Qt::Key_E ),
    KeyCodeMapEntry( "ok", 0xf72b, Qt::Key_K ),
    KeyCodeMapEntry( "mute", 0xc538, Qt::Key_U ),
    KeyCodeMapEntry( "src", 0xc538, Qt::Key_T ),
    KeyCodeMapEntry( "", 0x00, 0 ), // sentinal
};

Remote::Remote( QWidget* parent )
    : QWidget( 0,
	       Qt::FramelessWindowHint |
	       Qt::Tool
	), gui_( new Ui::Remote )
{
    setAttribute( Qt::WA_TranslucentBackground, true );
    setAttribute( Qt::WA_QuitOnClose, false );
    setAttribute( Qt::WA_StaticContents, true );
    setAutoFillBackground( false );

    //
    // Initialize the maps used to translate object names and Qt key code
    // values into remote control integer values.
    //
    int index = 0;
    while ( 1 ) {
	if ( inits[ index ].key == 0x00 )
	    break;
	nameKeyCodes_.insert(
	    NameKeyCodeMap::value_type( inits[ index ].name,
					inits[ index ].keyCode ) );
	keyKeyCodes_.insert(
	    KeyKeyCodeMap::value_type( inits[ index ].key,
				       inits[ index ].keyCode ) );
	++index;
    }

    //
    // Build the GUI. Connect all buttons to the same slot.
    //
    gui_->setupUi( this );
    connect( gui_->power, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->one, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->two, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->three, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->four, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->five, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->six, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->seven, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->eight, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->nine, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->zero, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->rewind, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->play, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->fastForward, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->pause, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->stop, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->left, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->right, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->up, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->down, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->volumeUp, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->volumeDown, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->brightnessUp, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->brightnessDown, SIGNAL( clicked() ),
	     SLOT( buttonPressed() ) );
    connect( gui_->disp, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->guide, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->menu, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->pip, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->rec, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->recall, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->sleep, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->ok, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
    connect( gui_->mute, SIGNAL( clicked() ), SLOT( buttonPressed() ) );
}

void
Remote::buttonPressed()
{
    //
    // Obtain the name of the button that was pressed. Use this as the key into
    // the keyCodes map to obtain the raw remote keycode to send.
    //
    QWidget* w = qobject_cast<QWidget*>( this->sender() );
    QString name = w->objectName();
    NameKeyCodeMap::const_iterator pos = nameKeyCodes_.find( name );
    if ( pos == nameKeyCodes_.end() ) {
	std::clog << "no keycode for " << name.toStdString() << '\n';
	return;
    }

    emit keyPressed( pos->second );
}

void
Remote::simulateButtonPressed( uint32_t key )
{
    KeyKeyCodeMap::const_iterator pos = keyKeyCodes_.find( key );
    if ( pos == keyKeyCodes_.end() ) {
	std::clog << "no keycode for " << key << '\n';
	return;
    }

    emit keyPressed( pos->second );
}

void
Remote::mousePressEvent( QMouseEvent* event )
{
    if ( event->button() == Qt::LeftButton ) {
        dragPosition_ = event->globalPos() - frameGeometry().topLeft();
        event->accept();
    }
}

void
Remote::mouseMoveEvent( QMouseEvent* event )
{
    if ( event->buttons() & Qt::LeftButton ) {
        move( event->globalPos() - dragPosition_ );
        event->accept();
    }
}

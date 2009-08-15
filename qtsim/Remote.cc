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

#include "MainWindow.h"
#include "Remote.h"

//
// Mapping elements from button name to remote keycode that an actual remote
// would emit.
//
static Remote::KeyCodeMap::value_type inits[] = {
    Remote::KeyCodeMap::value_type( "power", 0xf702 ),
    Remote::KeyCodeMap::value_type( "one", 0xf786 ),
    Remote::KeyCodeMap::value_type( "two", 0xf746 ),
    Remote::KeyCodeMap::value_type( "three", 0xf7c6 ),
    Remote::KeyCodeMap::value_type( "four", 0xf726 ),
    Remote::KeyCodeMap::value_type( "five", 0xf7a6 ),
    Remote::KeyCodeMap::value_type( "six", 0xf766 ),
    Remote::KeyCodeMap::value_type( "seven", 0xf7e6 ),
    Remote::KeyCodeMap::value_type( "eight", 0xf716 ),
    Remote::KeyCodeMap::value_type( "nine", 0xf796 ),
    Remote::KeyCodeMap::value_type( "zero", 0xf776 ),
    Remote::KeyCodeMap::value_type( "rewind", 0xf70e ),
    Remote::KeyCodeMap::value_type( "play", 0xf732 ),
    Remote::KeyCodeMap::value_type( "fastForward", 0xf76e ),
    Remote::KeyCodeMap::value_type( "pause", 0xf7b2 ),
    Remote::KeyCodeMap::value_type( "stop", 0xf7c2 ),
    Remote::KeyCodeMap::value_type( "left", 0xf74b ),
    Remote::KeyCodeMap::value_type( "right", 0xf7cb ),
    Remote::KeyCodeMap::value_type( "up", 0xf70b ),
    Remote::KeyCodeMap::value_type( "down", 0xf78b ),
    Remote::KeyCodeMap::value_type( "volumeUp", 0xf778 ),
    Remote::KeyCodeMap::value_type( "volumeDown", 0xf7f8 ),
    Remote::KeyCodeMap::value_type( "brightnessUp", 0xf70d ),
    Remote::KeyCodeMap::value_type( "brightnessDown", 0xf78d ),
    Remote::KeyCodeMap::value_type( "", 0x00 ), // sentinal
};

Remote::Remote()
    : QWidget(), gui_( new Ui::Remote )
{
    setWindowFlags( windowFlags() | Qt::Tool );

    int index = 0;
    while ( 1 ) {
	if ( inits[ index ].second == 0x00 )
	    break;
	keyCodes_.insert( inits[ index ] );
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
    KeyCodeMap::const_iterator pos = keyCodes_.find( name );
    if ( pos == keyCodes_.end() ) {
	std::clog << "no keycode for " << name.toStdString() << '\n';
	return;
    }

    emit keyPressed( pos->second );
}

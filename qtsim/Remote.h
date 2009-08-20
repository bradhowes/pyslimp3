#ifndef REMOTE_H // -*- C++ -*-
#define REMOTE_H

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

#include <map>

#include <QtGui/QWidget>

#include "ui_Remote.h"

class MainWindow;

class Remote : public QWidget
{
    Q_OBJECT
public:

    typedef std::map<QString,uint32_t> KeyCodeMap;

    Remote();

signals:

    void keyPressed( uint32_t keyCode );

public slots:

    void buttonPressed();

private:
    Ui::Remote* gui_;
    KeyCodeMap keyCodes_;
};

#endif
#ifndef PYSLIMP3_MAINWINDOW_H // -*- C++ -*-
#define PYSLIMP3_MAINWINDOW_H

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

#include <QtCore/QTime>
#include <QtCore/QDateTime>
#include <QtGui/QMainWindow>
#include <QtNetwork/QHostAddress>

class QTimer;
class QUdpSocket;

class Remote;
class VFDElement;
class VFDElementData;

class MainWindow : public QWidget
{
    Q_OBJECT
public:

    MainWindow();

public slots:

    void sendKey( uint32_t keyCode );

private slots:

    void emitHeartbeat();

    void emitDiscovery();

    void emitHello();

    void readMessage();

private:

    void mousePressEvent( QMouseEvent* event );
    void writeMessage( size_t count );
    void updateDisplay( qint64 size );
    void sendKeyMessage( uint32_t when, uint32_t keyCode );
    void writeInteger( uint32_t value, size_t offset );
    void dumpBuffer( qint64 size );
    void clearDisplay();

    QTime timeSource_;
    Remote* remote_;
    QList<VFDElementData*> bits_;
    QList<VFDElement*> row1_;
    QList<VFDElement*> row2_;
    QTimer* timer_;
    QUdpSocket* serverSocket_;
    unsigned char buffer_[ 2048 ];
    QHostAddress serverAddress_;
    QDateTime lastTimeStamp_;
};

#endif

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

#include <QtCore/QByteArray>
#include <QtCore/QTime>
#include <QtCore/QDateTime>
#include <QtGui/QMainWindow>
#include <QtNetwork/QHostAddress>

class QTimer;
class QUdpSocket;

class Remote;
class VFDElement;
class VFDElementData;

/** Main window for the qtsim application. Locates a Pyslimp3 server via UDP
    broadcast, processes display updates from the server, and sends remote
    controller key events to the server.

    The display consists of two lines of 40 VFDElement instances that simulate
    the vaccuum field display found in the original SLiMP3 unit. Each
    VFDElement has a pointer to a VFDElementData object that defines what bits
    to illuminate. There is a standard set of 128 characters defined, with the
    first 32 being customized by the Pyslimp3 server using certain control
    codes in the display message.
*/
class MainWindow : public QWidget
{
    Q_OBJECT
public:

    /** Constructor. Creates a Remote floating window, initializes the VFD
	display, and creates a socket for communicating with a Pyslimp3 server.
    */
    MainWindow();

public slots:

    /** Slot invoked when the user presses a button on the remote controller
        window.
	\param keyCode the SLiMP3 remote control key code to send to
        the Pyslimp3 server.
    */
    void sendKey( uint32_t keyCode );

private slots:

    /** Slot invoked when the heartbeat timer fires. Sends either a discovery
     * message or a hello message.
    */
    void emitHeartbeat();

    /** Slot invoked when a UDP message is available on the internal QUdpSocket
	instance, presumably from a Pyslimp3 server.
    */
    void readMessage();

private:

    /** Broadcast a SLiMP3 discovery message.
    */
    void emitDiscovery();
    
    /** Send a SLiMP3 hello message to the current server
    */
    void emitHello();
    
    /** Override of QWidget method. Show the remote window.
        \param event 
    */
    void mousePressEvent( QMouseEvent* event );
    
    /** Send out a broadcast or UDP message with the contents of the internal
        buffer, 
        \param buffer data to send
        \return true if successful, false otherwise
    */
    bool writeMessage( const QByteArray& data );
    void updateDisplay();
    void sendKeyMessage( uint32_t when, uint32_t keyCode );
    void writeInteger( QByteArray&, int index, uint32_t value );
    void dumpBuffer();
    void clearDisplay();
    void setDisplay( const std::string& line1, const std::string& line2 );
    void processEntry();
    void processCharacter();
    void processCommand();
    void processBrightness();
    void processCustomDefinition( uint8_t index );
    void keyPressEvent( QKeyEvent* event );
    void writeLine( const std::string& data );

    QTime timeSource_;
    Remote* remote_;
    QList<VFDElementData*> bits_;
    QList<VFDElement*> elements_;
    int elementIndex_;
    QTimer* timer_;
    QUdpSocket* serverSocket_;
    QByteArray inputBuffer_;
    int inputIndex_;
    QHostAddress serverAddress_;
    QDateTime lastTimeStamp_;
    bool foundServer_;
};

#endif

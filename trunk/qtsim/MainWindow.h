#ifndef PYSLIMP3_MAINWINDOW_H // -*- C++ -*-
#define PYSLIMP3_MAINWINDOW_H

//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

#include <QtGui/QMainWindow>

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
    void updateDisplay();
    void sendKeyMessage( uint32_t when, uint32_t keyCode );
    void writeInteger( uint32_t value, size_t offset );

    Remote* remote_;
    QList<VFDElementData*> bits_;
    QList<VFDElement*> row1_;
    QList<VFDElement*> row2_;
    QTimer* timer_;
    QUdpSocket* serverSocket_;
    char buffer_[ 2048 ];
    bool foundServer_;
};

#endif

#ifndef REMOTE_H // -*- C++ -*-
#define REMOTE_H

#include <map>

//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

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

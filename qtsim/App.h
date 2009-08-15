#ifndef PYSLIMP3_APP_H // -*- C++ -*-
#define PYSLIMP3_APP_H

//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

#include <QtGui/QApplication>

class MainWindow;

class App : public QApplication
{
    Q_OBJECT
public:

    App( int& argc, char** argv );

private:
    MainWindow* mainWindow_;
};

#endif

//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

#include "App.h"
#include "MainWindow.h"

App::App( int& argc, char** argv )
    : QApplication( argc, argv ), mainWindow_( new MainWindow )
{
    mainWindow_->show();
    mainWindow_->raise();
    mainWindow_->activateWindow();
}

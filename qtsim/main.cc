#include "App.h"

int
main( int argc, char** argv )
{
    App* app = new App( argc, argv );
    return app->exec();
}

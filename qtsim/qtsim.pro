QT += network 

CONFIG += uitools

FORMS += Remote.ui \

HEADERS += App.h \
           MainWindow.h \
           Remote.h \
           VFDElement.h \
           VFDElementData.h \

SOURCES += App.cc \
           MainWindow.cc \
           Remote.cc \
           VFDElement.cc \
           VFDElementData.cc \
           main.cc \

TARGET = qtsim

//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

#include <QtPlugin>

#include "VFDElement.h"
#include "VFDElementPlugin.h"

VFDElementPlugin::VFDElementPlugin(QObject *parent)
    : QObject( parent ), initialized_( false )
{
    ;
}

void
VFDElementPlugin::initialize( QDesignerFormEditorInterface* )
{
    if ( initialized_ ) return;
    initialized_ = true;
}

bool
VFDElementPlugin::isInitialized() const
{
    return initialized_;
}

QWidget*
VFDElementPlugin::createWidget( QWidget *parent )
{
    return new VFDElement( parent );
}

QString
VFDElementPlugin::name() const
{
    return "VFDElement";
}

QString
VFDElementPlugin::group() const
{
    return "Pyslimp3 Widgets";
}

QIcon
VFDElementPlugin::icon() const
{
    return QIcon();
}

QString
VFDElementPlugin::toolTip() const
{
    return "";
}

QString
VFDElementPlugin::whatsThis() const
{
    return "";
}

bool
VFDElementPlugin::isContainer() const
{
    return false;
}

QString
VFDElementPlugin::domXml() const
{
    return "<widget class=\"VFDElement\" name=\"vfdElement\">\n"
           " <property name=\"geometry\">\n"
           "  <rect>\n"
           "   <x>0</x>\n"
           "   <y>0</y>\n"
           "   <width>100</width>\n"
           "   <height>100</height>\n"
           "  </rect>\n"
           " </property>\n"
           " <property name=\"toolTip\" >\n"
           "  <string>The current time</string>\n"
           " </property>\n"
           " <property name=\"whatsThis\" >\n"
           "  <string>The analog clock widget displays "
           "the current time.</string>\n"
           " </property>\n"
           "</widget>\n";
}

QString VFDElementPlugin::includeFile() const
{
    return "VFDElement.h";
}

Q_EXPORT_PLUGIN2( customwidgetplugin , VFDElementPlugin )

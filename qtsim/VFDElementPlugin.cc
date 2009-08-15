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

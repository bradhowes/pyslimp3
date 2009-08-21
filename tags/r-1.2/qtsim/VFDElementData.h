#ifndef PYSLIMP3_VFDELEMENTDATA_H // -*- C++ -*-
#define PYSLIMP3_VFDELEMENTDATA_H

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

#include <vector>

#include <QtCore/QObject>

class VFDElementData : public QObject
{
    Q_OBJECT
public:

    enum { kRows = 8, kColumns = 5 };

    typedef int RawDef[ kRows ];

    VFDElementData();

    VFDElementData( const RawDef& data );

    void setBits( const RawDef& data );

    void setBits( const std::vector<int>& data );

    bool isSet( int row, int column ) const;

signals:

    void changed();

private:

    void init();

    std::vector<int> data_;
    std::vector<int> bits_;
};

#endif

#ifndef PYSLIMP3_VFDELEMENTDATA_H // -*- C++ -*-
#define PYSLIMP3_VFDELEMENTDATA_H

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

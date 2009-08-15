#ifndef PYSLIMP3_VFDELEMENT_H // -*- C++ -*-
#define PYSLIMP3_VFDELEMENT_H

//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

#include <QtDesigner/QDesignerExportWidget>
#include <QtGui/QWidget>

class VFDElementData;

class QDESIGNER_WIDGET_EXPORT VFDElement : public QWidget
{
    typedef QWidget Super;
    Q_OBJECT
    Q_PROPERTY( QColor onColor READ getOnColor WRITE setOnColor );
    Q_PROPERTY( QColor onColor READ getOnColor WRITE setOnColor );
    Q_PROPERTY( QColor offColor READ getOffColor WRITE setOffColor );
    Q_PROPERTY( QColor offColor READ getOffColor WRITE setOffColor );
    Q_PROPERTY( QColor backgroundColor READ getBackgroundColor WRITE setBackgroundColor );
    Q_PROPERTY( int pixelSize READ getPixelSize WRITE setPixelSize );
    Q_PROPERTY( int spacing READ getSpacing WRITE setSpacing );

public:

    VFDElement( QWidget* parent = 0 );

    QColor getOnColor() const { return onColor_; }
    QColor getOffColor() const { return offColor_; }
    QColor getBackgroundColor() const { return backgroundColor_; }
    int getPixelSize() const { return pixelSize_; }
    int getSpacing() const { return spacing_; }

    QSize minimumSizeHint() const { return getSize(); }
    QSize sizeHint() const { return getSize(); }

public slots:

    void setOnColor( QColor color );
    void setOffColor( QColor color );
    void setBackgroundColor( QColor color );
    void setPixelSize( int value );
    void setSpacing( int value );
    void setData( VFDElementData* data, int brightness );

private:

    void paintEvent( QPaintEvent* event );
    QSize getSize() const;

    QColor onColor_;
    QColor offColor_;
    QColor backgroundColor_;
    QColor adjustedOnColor_;
    int pixelSize_;
    int spacing_;
    VFDElementData* data_;
    int brightness_;
};

#endif

#ifndef PYSLIMP3_VFDELEMENTPLUGIN_H // -*- C++ -*-
#define PYSLIMP3_VFDELEMENTPLUGIN_H

//
// (C) Copyright 2009 Massachusetts Institute of Technology. All rights
// reserved.
//

class VFDElementPlugin : public QObject, public QDesignerCustomWidgetInterface
{
    Q_OBJECT
    Q_INTERFACES( QDesignerCustomWidgetInterface )
public:

    VFDElementPlugin( QObject* parent = 0 );

    bool isContainer() const;

    bool isInitialized() const;

    QIcon icon() const;

    QString domXml() const;

    QString group() const;

    QString includeFile() const;

    QString name() const;

    QString toolTip() const;

    QString whatsThis() const;

    QWidget *createWidget(QWidget *parent);

    void initialize(QDesignerFormEditorInterface *core);

private:
    bool initialized_;
};

#endif

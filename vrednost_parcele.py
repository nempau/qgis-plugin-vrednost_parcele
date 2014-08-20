# -*- coding: utf-8 -*-
"""
/***************************************************************************
 vrednost_parcele
                                 A QGIS plugin
 nema
                              -------------------
        begin                : 2014-08-05
        copyright            : (C) 2014 by nemanja
        email                : paunicnemanja@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
import shutil
import os
import qgis.utils
from qgis.gui import * 
from qgis.analysis import *
import processing
# Import the code for the dialog
from vrednost_parceledialog import vrednost_parceleDialog

class vrednost_parcele:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.settings = QSettings()
       

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/vrednost_parcele/icon.png"),
            u"nemam ni to", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu("&Vrednost_Parcele", self.action)

    def unload(self):
        self.iface.removePluginVectorMenu("&Create labeled layer",self.action)
        self.iface.removeToolBarIcon(self.action)
       

    # run method that performs all the real work
    def run(self):
        
        self.savelayerPath = ""
    
        # create and show the dialog
        self.dlg = vrednost_parceleDialog()    
        
        QObject.connect(self.dlg.ui.pushButtonUcitaj1, SIGNAL('clicked()'), self.createLayerPath1)
        QObject.connect(self.dlg.ui.pushButtonUcitaj2, SIGNAL('clicked()'), self.createLayerPath2)
        QObject.connect(self.dlg.ui.pushButtonUcitaj3, SIGNAL('clicked()'), self.createLayerPath3)
        
       
    
        # show the dialog
        self.dlg.show()
        
    def createLayerPath1(self):
        self.dlg.ui.lineEditPutanjaParcele.clear()
        lastDir1 = self.settings.value("/LabelLayer/lastDir1")
        self.savelayerPath1 = QFileDialog.getOpenFileName(None,"UÄŤitaj parcele", lastDir1, "*.shp")
        if not self.savelayerPath1:
            return
        self.dlg.ui.lineEditPutanjaParcele.setText(self.savelayerPath1)
        file_info1 = QFileInfo(self.savelayerPath1)
        self.layer_name1 = file_info1.completeBaseName()
        self.layer_dir1 = file_info1.absolutePath()
        self.settings.setValue("/LabelLayer/lastDir1", str(self.layer_dir1))
        label_layer1 = QgsVectorLayer(self.savelayerPath1, self.layer_name1, "ogr" )
        QgsMapLayerRegistry.instance().addMapLayer(label_layer1)
        
        
                
    def createLayerPath2(self):
        self.dlg.ui.lineEditPutanjaProcembeni.clear()
        lastDir2 = self.settings.value("/LabelLayer/lastDir2")
        self.savelayerPath2 = QFileDialog.getOpenFileName(None,"UÄŤitaj procembene razrede", lastDir2, "*.shp")
        if not self.savelayerPath2:
            return
        self.dlg.ui.lineEditPutanjaProcembeni.setText(self.savelayerPath2)
        file_info2 = QFileInfo(self.savelayerPath2)
        self.layer_name2 = file_info2.completeBaseName()
        self.layer_dir2 = file_info2.absolutePath()
        self.settings.setValue("/LabelLayer/lastDir2", str(self.layer_dir2))
        label_layer2 = QgsVectorLayer(self.savelayerPath2, self.layer_name2, "ogr" )
        QgsMapLayerRegistry.instance().addMapLayer(label_layer2)
       
        



    def createLayerPath3(self):
        self.dlg.ui.lineEditPutanjaIzlazni.clear()
        lastDir3 = self.settings.value("/LabelLayer/lastDir3")
        self.savelayerPath3 = QFileDialog.getSaveFileName(None,"Create output shapefile", lastDir3, "*.shp")
        if not self.savelayerPath3:
            return
        self.dlg.ui.lineEditPutanjaIzlazni.setText(self.savelayerPath3)
        file_info3 = QFileInfo(self.savelayerPath3)
        self.layer_name3 = file_info3.completeBaseName()
        self.layer_dir3 = file_info3.absolutePath()
        self.settings.setValue("/LabelLayer/lastDir3", str(self.layer_dir3))
        self.intersect()
        label_layer3 = QgsVectorLayer(self.savelayerPath3, self.layer_name3, "ogr" )
        trecilayer = QgsMapLayerRegistry.instance().addMapLayer(label_layer3)
        
        # moj dodatak
        name = "noviAtribut" 
        provider = trecilayer.dataProvider()
        caps = provider.capabilities()
        # Check if attribute is already there, return "-1" if not
        ind = provider.fieldNameIndex(name)
        try:
            if ind == -1:
                if caps & QgsVectorDataProvider.AddAttributes:
                    res = provider.addAttributes( [ QgsField(name,QVariant.Double) ] )
        except:
            return False
        trecilayer.updateFields()
        # Zamisljam da sam koeficijente ucitao iz ulaznog fajla
        koef=[1.00, 0.85, 0.80, 0.75, 0.70, 0.60, 0.50, 0.40, 0.00]
        
        # Pokugi redove
        iter=trecilayer.getFeatures()
        
        for red in iter:
            razred=red.Procembeni()
            povrsina=red.AreaI_0()
            nova=povrsina*koef(razred-1)
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                attrs = {-1 : red }
                trecilayer.dataProvider().changeAttributeValues({ red : attrs })
        
        

    def intersect(self):
        canvas = qgis.utils.iface.mapCanvas()
        layers = canvas.layers()
        layer1 = canvas.layer(0)
        layer2 = canvas.layer(1)
        overlayAnalyzer = QgsOverlayAnalyzer()
        overlayAnalyzer.intersection(layer2, layer1, self.savelayerPath3, False)


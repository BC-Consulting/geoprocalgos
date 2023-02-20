# -*- coding: utf-8 -*-
"""
/***************************************************************************
                            A QGIS Processing plugin
                             GeoProc.com algorithms

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-05-19
        copyright            : (C) 2019-2023 by GeoProc.com
        email                : info@geoproc.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
WARNING: code formatting does not follow pycodestyle recommendations
"""

__author__ = 'GeoProc.com'
__date__ = '2019-05-19'
__copyright__ = '(C) 2019-2023 by GeoProc.com'
__revision__ = '$Format:%H$'

import os
import sys
import inspect

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QObject

from qgis.core import QgsApplication
import processing
from .GeoProc_provider import geoprocProvider
from .GeoProc_provider import thelists

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class PPlugins(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        self.provider = None
        self.iface = iface
        self.actions = []

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = geoprocProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()
        self.toolbar = self.iface.addToolBar(u'GeoProc')
        self.toolbar.setObjectName(u'GeoProc')
        self.toolbar.setToolTip(u'GeoProc Processing algos')

        mylists = thelists()
        icos = mylists.get_icons()
        dsc = mylists.get_tooltips()
        self.algos = mylists.get_algo()
        for i, alg in enumerate(mylists.get_alglist()):
            icon = os.path.join(os.path.join(cmd_folder, 'res', icos[i]+'.png'))
            action = QAction(QIcon(icon), dsc[i], self.iface.mainWindow())
            action.triggered.connect(self.run)
            self.iface.addPluginToMenu(u"&GeoProc", action)
            self.toolbar.addAction(action)
            self.actions.append(action)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        for action in self.actions:
            self.iface.removePluginMenu(u"&GeoProc", action)
        parent = self.toolbar.parentWidget()
        parent.removeToolBar(self.toolbar)
        
    def run(self):
        algo = self.sender().text()
        processing.execAlgorithmDialog("GeoProc:"+self.algos[algo])
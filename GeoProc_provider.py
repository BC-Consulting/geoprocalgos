# -*- coding: utf-8 -*-
"""
/***************************************************************************
                        A QGIS Processing plugin provider
                           for GeoProc.com algorithms

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-05-19
        copyright            : (C) 2019 by GeoProc.com
        email                : info@geoproc.com
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

__author__ = 'GeoProc.com'
__date__ = '2019-05-19'
__copyright__ = '(C) 2019 by GeoProc.com'
__revision__ = '$Format:%H$'

import os
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider

from .bcCBar_algorithm             import bcCBarAlgorithm
from .bcSaveqml_algorithm          import bcSaveqmlAlgorithm
from .bcMultiStyles_algorithm      import bcMultiStylesAlgorithm
from .bcStackP_algorithm           import bcStackPAlgorithm
from .bcGenRNDSurveyData_algorithm import bcGenRNDSurveyDataAlgorithm
from .bcclr2tbl_algorithm          import bcclr2tblAlgorithm
from .bcSwapYZ_algorithm           import bcSwapYZAlgorithm

plugin_path = os.path.dirname(__file__)

class geoprocProvider(QgsProcessingProvider):

    def __init__(self):
        """ Initialisation. """
        #
        super().__init__()

        # Load algorithms
        self.alglist = [bcCBarAlgorithm(),
                        bcSaveqmlAlgorithm(),
                        bcMultiStylesAlgorithm(),
                        bcStackPAlgorithm(),
                        bcclr2tblAlgorithm(),
                        bcSwapYZAlgorithm(),
                        bcGenRNDSurveyDataAlgorithm(),
                       ]
    #-------------------------------------------------------------------------------------

    def icon(self):
        """ Returns a QIcon for the algorithm. """
        #
        return QIcon(os.path.join(plugin_path, 'res/geoproc.svg'))
    #-------------------------------------------------------------------------------------

    def svgIconPath(self):
        """ Returns a path to an SVG version of the algorithm's icon. """
        #
        return os.path.join(plugin_path, 'res/geoproc.svg')
    #-------------------------------------------------------------------------------------

    def unload(self):
        """ Unloads the provider. Any tear-down steps required by the provider should be 
            implemented here.
        """
        #
        pass
    #-------------------------------------------------------------------------------------

    def loadAlgorithms(self):
        """ Loads all algorithms belonging to this provider. """
        #
        for alg in self.alglist:
            self.addAlgorithm( alg )
    #-------------------------------------------------------------------------------------

    def id(self):
        """ Returns the unique provider id, used for identifying the provider. """
        #
        return 'GeoProc'
    #-------------------------------------------------------------------------------------

    def name(self):
        """ Returns the provider name, which is used to describe the provider within
            the GUI. """
        #
        return 'GeoProc'
    #-------------------------------------------------------------------------------------

    def longName(self):
        """ Returns a longer version of the provider name. """
        #
        return 'GeoProc provider: collection of QGIS V3.x Processing algorithms.'
#=========================================================================================
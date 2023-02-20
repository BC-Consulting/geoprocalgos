# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bcCBar
                                 A QGIS plugin
 Create a colour scalebar for Composer
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'GeoProc.com'
__date__ = '2019-05-19'
__copyright__ = '(C) 2019-2023 by GeoProc.com'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load bcCBar class from file bcCBar.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .GeoProcAlgos import PPlugins
    return PPlugins(iface)

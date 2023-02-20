# -*- coding: utf-8 -*-
"""
Little function to handle qparam creation

Kind of object handled by routine:
                        Options
    Bool               : {'defaultValue':True}
    CRS
    Enum
    EXTENT
    Field
    File               : {'ext'':'HTML'} or {'fileFilter':'HTML files (*.html), All files (*.*)'}
    FileDestination
    FolderDestination
    MLayer
    MultipleLayers
    NumberD            : {'defaultValue':0., 'minValue':0., 'maxValue':1.}
    NumberI            : {'defaultValue':0, 'minValue':0, 'maxValue':1}
    Point
    RasterLayer
    SINK
    String             : {'defaultValue':''}
    VectorLayer

@author: benoit
        begin                : 2019-05-19
        copyright            : (C) 2019-2023 by GeoProc.com
        email                : info@geoproc.com
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

from qgis.core import (
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterMapLayer,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString,
                       )

dicoparams = {
                        'Bool':QgsProcessingParameterBoolean,
                         'CRS':QgsProcessingParameterCrs,
                      'EXTENT':QgsProcessingParameterExtent,
                       'Field':QgsProcessingParameterField,
                        'File':QgsProcessingParameterFile,
             'FileDestination':QgsProcessingParameterFileDestination,
           'FolderDestination':QgsProcessingParameterFolderDestination,
           'RasterDestination':QgsProcessingParameterRasterDestination,
                      'MLayer':QgsProcessingParameterMapLayer,
              'MultipleLayers':QgsProcessingParameterMultipleLayers,
                     'NumberD':QgsProcessingParameterNumber,
                     'NumberI':QgsProcessingParameterNumber,
                       'Point':QgsProcessingParameterPoint,
                 'RasterLayer':QgsProcessingParameterRasterLayer,
                        'SINK':QgsProcessingParameterFeatureSink,
                      'String':QgsProcessingParameterString,
                 'VectorLayer':QgsProcessingParameterFeatureSource,
             }

FlagsAdv = QgsProcessingParameterDefinition.FlagAdvanced

def set_param(param, the_params):
    ''' Creates a QgsProcessingParameter and returns it. '''
    #
    arg      = the_params[param]
    what     = arg[2]
    optional = arg[4]
    the_str  = arg[1]
    qparam   = None
    dico     = {'optional':optional}
    TT       = ''
    #
    if 'defaultValue' in arg[3]: dico['defaultValue'] = arg[3]['defaultValue']
    if 'minValue'     in arg[3]: dico['minValue'] = arg[3]['minValue']
    if 'maxValue'     in arg[3]: dico['maxValue'] = arg[3]['maxValue']
    if 'types'        in arg[3]: dico['types'] = arg[3]['types']
    if 'layerType'    in arg[3]: dico['layerType'] = arg[3]['layerType']
    if 'FILTER'       in arg[3]: dico['fileFilter'] = arg[3]['FILTER']
    if 'ext'          in arg[3]: dico['extension'] = arg[3]['ext']
    if 'parent'       in arg[3]: dico['parentLayerParameterName']=arg[3]['parent']
    if 'type'         in arg[3]: dico['type'] = arg[3]['type']
    if   what == 'NumberD':      dico['type'] = QgsProcessingParameterNumber.Double
    elif what == 'NumberI':      dico['type'] = QgsProcessingParameterNumber.Integer
    #
    if what in dicoparams:
        qparam = dicoparams[what](param, the_str, **dico)
    elif what == 'Enum':
        qparam = QgsProcessingParameterEnum(
                                            param,
                                            the_str,
                                            [s for s in arg[3]['list']],
                                            **dico
                                           )
    if qparam != None:
        if TT != '':
            qparam.toolTip = TT
        if 100 <= arg[0] < 1000:
            qparam.setFlags(qparam.flags() | FlagsAdv)
        return qparam
    #
    return None
#=========================================================================================

def IsNum(v, the_layer):
    ''' Check that field (v) of layer (the_layer) is numeric. '''
    #
    f = the_layer.fields().at(the_layer.fields().lookupField(v))
    return f.isNumeric()
#=========================================================================================


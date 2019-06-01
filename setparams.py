# -*- coding: utf-8 -*-
"""
Little function to handle qparam creation
@author: benoit
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
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString,
                       )

FlagsAdv = QgsProcessingParameterDefinition.FlagAdvanced

def set_param(param, the_params):
    ''' Creates a QgsProcessingParameter parameter and returns it. '''
    #
    arg      = the_params[param]
    what     = arg[2]
    optional = arg[4]
    the_str  = arg[1]
    qparam   = None
    #
    if what == 'RasterLayer':
        qparam = QgsProcessingParameterRasterLayer(
                 param,
                 the_str,
                 optional = optional
                 )
    elif what == 'VectorLayer':
        qparam = QgsProcessingParameterFeatureSource(
                 param,
                 the_str,
                 types = arg[3]['types'],
                 optional = optional
                 )
    elif what == 'MultipleLayers':
        qparam = QgsProcessingParameterMultipleLayers(
                param,
                the_str,
                layerType = arg[3]['layerType'],
                optional = optional
                )
    elif what == 'File':
        qparam = QgsProcessingParameterFile(
                 param,
                 the_str,
                 extension = arg[3]['ext'],
                 optional = optional
                 )
    elif what == 'Field':
        qparam = QgsProcessingParameterField(
                 param,
                 the_str,
                 parentLayerParameterName=arg[3]['parent'],
                 optional = optional
                 )
    elif what == 'Enum':
        qparam = QgsProcessingParameterEnum(
                 param,
                 the_str,
                 [s for s in arg[3]['list']],
                 defaultValue = arg[3]['defaultValue'],
                 optional = optional
                 )
    elif what == 'String':
        qparam = QgsProcessingParameterString(
                 param,
                 the_str,
                 defaultValue = arg[3]['defaultValue'],
                 optional = optional
                 )
    elif what == 'NumberD':
        qparam = QgsProcessingParameterNumber(
                 param,
                 the_str,
                 type = QgsProcessingParameterNumber.Double,
                 defaultValue = arg[3]['defaultValue'],
                 minValue = arg[3]['minValue'],
                 maxValue = arg[3]['maxValue'],
                 optional = optional
                 )                
    elif what == 'NumberI':
        qparam = QgsProcessingParameterNumber(
                 param,
                 the_str,
                 type = QgsProcessingParameterNumber.Integer,
                 defaultValue = arg[3]['defaultValue'],
                 minValue = arg[3]['minValue'],
                 maxValue = arg[3]['maxValue'],
                 optional = optional
                 )                
    elif what == 'Bool':
        qparam = QgsProcessingParameterBoolean(
                 param,
                 the_str,
                 defaultValue = arg[3]['defaultValue'],
                 optional = optional
                 )                
    elif what == 'FileDestination':
        qparam = QgsProcessingParameterFileDestination(
                 param,
                 the_str,
                 defaultValue = arg[3]['defaultValue'],
                 fileFilter = arg[3]['FILTER'],
                 optional = optional
                 )
    elif what == 'CRS':
        qparam =  QgsProcessingParameterCrs(
                  param,
                  the_str,
                  defaultValue = arg[3]['defaultValue'],
                  optional = optional
                  )
    elif what == 'EXTENT':
        qparam =  QgsProcessingParameterExtent(
                  param,
                  the_str,
                  optional = optional
                  )
    #
    elif what == 'SINK':
        qparam =  QgsProcessingParameterFeatureSink(
                  param,
                  the_str,
                  type = arg[3]['type'],
                  optional = optional
                  )
    #
    if qparam != None:
        if arg[0] < 1000:
            qparam.setFlags(qparam.flags() | FlagsAdv)
        return qparam
    #
    return None
#=========================================================================================

# -*- coding: utf-8 -*-
"""
Little function to handle qparam creation

    Bool
    CRS
    Enum
    EXTENT
    Field
    File
    FileDestination
    FolderDestination
    MLayer
    MultipleLayers
    NumberD
    NumberI
    RasterLayer
    SINK
    String
    VectorLayer
    
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
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterMapLayer,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterNumber,
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
                      'MLayer':QgsProcessingParameterMapLayer,
              'MultipleLayers':QgsProcessingParameterMultipleLayers,
                     'NumberD':QgsProcessingParameterNumber,
                     'NumberI':QgsProcessingParameterNumber,
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
        if 100 <= arg[0] < 1000:
            qparam.setFlags(qparam.flags() | FlagsAdv)
        return qparam
    #
    return None
#=========================================================================================

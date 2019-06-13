# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bcMultiStyles3
                           A QGIS Processing algorithm
                        Load/Save all styles from a layer

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

import os, codecs, uuid
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessingAlgorithm,
                       QgsMapLayerStyle,
                       QgsProcessingUtils)

from .setparams import set_param
from .HelpbcA import help_bcMultiStyles

is_dependencies_satisfied = True
#-----------------------------------------------------------------------------------------
plugin_path = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'geoprocAlgos')

the_url = 'http://www.geoproc.com/free/bcMultiStyles3.htm'
help_string = help_bcMultiStyles
the_tags = ['qml','style','multi','layer','save','load']
#-----------------------------------------------------------------------------------------

class bcMultiStylesAlgorithm(QgsProcessingAlgorithm):
    ''' Processing wrapper. '''
    #
    # Parameters used for stacking profiles
    THE_LAYER = 'THE_LAYER'
    IS_SAVE   = 'IS_SAVE'
    IS_FORCE  = 'IS_FORCE'
    QML_DIR   = 'QML_DIR'
    OUTPUT    = 'OUTPUT'
    DEP       = 'DEP'

    _default_output = ''

    _the_strings = {"ALGONAME":"Multi-styles",
                    "ERR":"ERROR",
                    "ERR_DEP":"numpy and pandas are required to run this algorithm",
                    "DEP_LST":"numpy, pandas",
                    "H1":"Multi-styles operation results on:",
                    "SAVE":"Operation: save multi-styles to qml files.",
                    "LOAD":"Operation: load styles from multiple qml files.",
                    "O1":"is saved.",
                    "O2":"is loaded.",
                    "N1":"could not be saved.",
                    "N2":"could not be loaded.",
                    "PATH":"Path where .qml's are located:",
                   }

    _pstr = ['Input layer',
             'Save',
             'qml directory',
             'Output Result file',
             'Result file (*.htm)',
             'Force load']

    def __init__(self):
        super().__init__()
    #-------------------------------------------------------------------------------------

    def _define_params(self):
        ''' Define parameters needed. '''
        #
        #       [0] < 100  : "normal" parameter
        # 100 < [0] < 1000 : Advanced Parameter
        #       [0] > 1000 : Output parameter
        self.the_params = {
           self.THE_LAYER: [1,self._pstr[0],'MLayer',{},False],
           self.IS_SAVE:   [2,self._pstr[1],'Bool',{'defaultValue':False},False],
           self.IS_FORCE:  [3,self._pstr[5],'Bool',{'defaultValue':False},True],
           self.QML_DIR:   [4,self._pstr[2],'FolderDestination',{},True],
           self.OUTPUT:    [1001,self._pstr[3],'FileDestination',
                            {'FILTER':self._pstr[4],'defaultValue':self._default_output},
                            True]
        }
        self._err_param = {self.DEP: [1,self._the_strings["ERR_DEP"],'String',
                           {'defaultValue':self._the_strings["DEP_LST"]},False]}
    #-------------------------------------------------------------------------------------

    def _create_HTML(self, pth, layer, outputFile):
        ''' Generate an output html file to show results. '''
        #
        with codecs.open(outputFile, 'w', encoding='utf-8') as f:
            f.write('<html>\n<head>\n')
            f.write('<meta http-equiv="Content-Type" content="text/html;') 
            f.write(' charset=utf-8" />\n</head>\n<body>\n')
            f.write('<h1>%s<br/>\n' % self._the_strings['H1'])
            f.write('%s</h1>\n' % layer)
            if self._error != '':
                f.write('<h2 style="color:red;">%s</h2>\n' % self._the_strings['ERR'])
                f.write('<p style="color:red;">%s</p>\n' % self._error)
            #
            else:
                f.write('<p>%s <a href="file:///%s">' % (self._the_strings['PATH'], pth))
                f.write('%s</a></p>\n' % pth)
                f.write('<p>%s</p>\n' % self._results)
            f.write('</body>\n</html>\n')
        #
        return outputFile
    #-------------------------------------------------------------------------------------

    def initAlgorithm(self, config):
        ''' Here we define the inputs and output of the algorithm. '''
        #
        self._define_params()
        if is_dependencies_satisfied:
            # Prepare all parameters needed for plotting the colour bar
            for param in sorted(self.the_params, key=self.the_params.__getitem__):
                b = self.the_params[param][0]
                qparam = set_param(param, self.the_params)
                if qparam != None:
                    if b < 100:
                        self.addParameter(qparam)
                    elif b < 1000:
                        self.addParameter((qparam))
                    else:
                        self.addParameter(qparam, True)

        else:
            qparam = set_param(self.DEP, self._err_param)
            self.addParameter(qparam)
        #
        self._tmpDir  = QgsProcessingUtils.tempFolder()
        self._results = ''
        self._error  = ''
    #-------------------------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        ''' Here is where the processing itself takes place. '''
        #
        if not is_dependencies_satisfied:
            return {}

        tmpf = str(uuid.uuid4())
        res_file = os.path.join(self._tmpDir, tmpf + '.htm')
        self._error = ''

        the_layer = self.parameterAsLayer(parameters, self.THE_LAYER, context)
        is_save   = self.parameterAsBool(parameters, self.IS_SAVE, context)
        is_force  = self.parameterAsBool(parameters, self.IS_FORCE, context)
        qml_path  = self.parameterAsFile(parameters, self.QML_DIR, context)
        if qml_path == '' or self._tmpDir in qml_path:
            qml_path = os.path.split(the_layer.source())[0]
            if not os.path.exists(qml_path):
                qml_path = self._tmpDir

        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if (self._default_output in output_file) or (output_file == ''):
            output_file = res_file
        else:
            output_file = os.path.splitext(output_file)[0] + '.htm'

        style_manager = the_layer.styleManager()
        lname = the_layer.name()

        # read valid style from layer
        style = QgsMapLayerStyle()
        style.readFromLayer(the_layer)

        c_style = style_manager.currentStyle()
        if is_save:
            # Save to files
            self._results = '<strong>%s</strong><br/>\n' % self._the_strings['SAVE']
            for style_name in style_manager.styles():
                style_manager.setCurrentStyle(style_name)
                the_qml = os.path.join(qml_path, the_layer.name()+'_'+style_name+".qml")
                _, flg = the_layer.saveNamedStyle(the_qml)
                if flg:
                    self._results+='%s: %s<br/>\n' % (style_name, self._the_strings['O1'])
                else:
                    self._results+='%s: %s<br/>\n' % (style_name, self._the_strings['N1'])
        #
        else:
            # Load from files  -  format should be: LayerName_StyleName.qml
            # Adapted from answer at: https://gis.stackexchange.com/questions/288341
            self._results = '<strong>%s</strong><br/>\n' % self._the_strings['LOAD']
            #
            for qml_file in [f for f in os.listdir(qml_path)
                             if os.path.isfile(os.path.join(qml_path, f)) and
                             f.endswith('.qml') and (is_force or (not is_force and
                             lname.lower() in os.path.splitext(f)[0].lower()))]:
                # get style name from filename
                if not is_force:
                    # style name from sidecar
                    bare = os.path.splitext(qml_file)[0]
                    if bare.lower() != lname.lower():
                        bare = bare.replace(lname, '')
                    else:
                        bare = '_default'
                    style_name = bare[1:]
                else:
                    # style name from generic qml
                    style_name = os.path.splitext(qml_file)[0]
                #
                style_manager.addStyle(style_name, style)
                style_manager.setCurrentStyle(style_name)
                _, b = the_layer.loadNamedStyle(os.path.join(qml_path, qml_file))
                if not b:
                    style_manager.removeStyle(style_name)
                    self._results+='%s: %s<br/>\n' % (style_name, self._the_strings['N2'])
                else:
                    self._results+='%s: %s<br/>\n' % (style_name, self._the_strings['O2'])
        style_manager.setCurrentStyle(c_style)
        fil = self._create_HTML(qml_path, the_layer.source(), output_file)
        #
        return {self.OUTPUT:fil}
    #-------------------------------------------------------------------------------------

    def get_error(self):
        ''' Return the error value. '''
        #
        return self.tr(self._error)
    #-------------------------------------------------------------------------------------

    def icon(self):
        ''' Returns a QIcon for the algorithm. '''
        #
        return QIcon(os.path.join(plugin_path, 'res', 'bcMultiStyles.svg'))
    #-------------------------------------------------------------------------------------

    def svgIconPath(self):
        ''' Returns a path to an SVG version of the algorithm's icon. '''
        #
        return os.path.join(plugin_path, 'res', 'bcMultiStyles.svg')
    #-------------------------------------------------------------------------------------

    def helpUrl(self):
        ''' Returns a url pointing to the algorithm's help page. '''
        #
        return the_url
    #-------------------------------------------------------------------------------------

    def shortHelpString(self):
        ''' Returns a localised short helper string for the algorithm. '''
        #
        return self.tr(help_string)
    #-------------------------------------------------------------------------------------

    def name(self):
        '''
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'bcMultiStyles3'
    #-------------------------------------------------------------------------------------

    def displayName(self):
        '''
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        '''
        return self.tr(self._the_strings["ALGONAME"])
    #-------------------------------------------------------------------------------------

    def tags(self):
        return self.tr(the_tags)
    #-------------------------------------------------------------------------------------

    def group(self):
        '''
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        '''
        return str(self.groupId()).capitalize()
    #-------------------------------------------------------------------------------------

    def groupId(self):
        '''
        One of: composer, layer, query, raster, survey, vector
        '''
        return 'layers'
    #-------------------------------------------------------------------------------------

    def tr(self, string):
        ''' No translation of strings. '''
        #
        return string
    #-------------------------------------------------------------------------------------

    def createInstance(self):
        ''' Creates a new instance of the algorithm class. '''
        #
        return bcMultiStylesAlgorithm()
    #-------------------------------------------------------------------------------------
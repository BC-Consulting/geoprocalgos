# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bcCBar3
                           A QGIS Processing algorithm
                      Create a colour scalebar for Composer

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-05-19
        copyright            : (C) 2019-2022 by GeoProc.com
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
__copyright__ = '(C) 2019-2022 by GeoProc.com'
__revision__ = '$Format:%H$'

import os, codecs, uuid
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingUtils,
                       QgsProcessingException)

from .setparams import set_param
from .cbar import drawCBar, cbar_usage
from .QgsBcUtils import check_oneband, check_color

# Check for dependencies
from .cbar import is_bs4_available, is_mpl_available
is_dependencies_satisfied = is_bs4_available and is_mpl_available
#-----------------------------------------------------------------------------------------

plugin_path = os.path.dirname(__file__)

the_url = 'https://www.geoproc.com/free/bccbar4.htm'
svg_note = """<p>"It is known that some vector graphics viewers (svg and pdf)
renders white gaps between segments of the colorbar. This is due to bugs in the viewers,
not Matplotlib."<br/>\n<em>source: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.
colorbar.html</em></p>\n"""
help_string = cbar_usage + '\n' + svg_note
the_tags = ['colour','color','colourbar','colorbar','scale','bar','scalebar','raster',
            '1-band','one-band','oneband','composer','svg','print','legend']
#-----------------------------------------------------------------------------------------

class bcCBarAlgorithm(QgsProcessingAlgorithm):
    ''' Processing wrapper for the colour scale bar algorithm. '''
    #
    # Parameters used for drawing the colour scale bar
    THE_LAYER     = 'THE_LAYER'
    ORI           = 'ORI'
    TITLE         = 'TITLE'
    DECI          = 'DECI'
    CLENGTH       = 'CLENGTH'
    CWIDTH        = 'CWIDTH'
    DEDGES        = 'DEDGES'
    TICKSEP       = 'TICKSEP'
    LABEL_ON      = 'LABEL_ON'
    LABEL_ALT     = 'LABEL_ALT'
    FONT_SIZE     = 'FONT_SIZE'
    TITLE_COLOR   = 'TITLE_COLOR'
    TITLE_FONT    = 'TITLE_FONT'
    TITLE_WEIGHT  = 'TITLE_WEIGHT'
    TICKFONTSIZE  = 'TICKFONTSIZE'
    TICKCOLO      = 'TICKCOLO'
    TICKLENGTH    = 'TICKLENGTH'
    TWK_REPLACE   = 'TWK_REPLACE'
    TWK_ADD       = 'TWK_ADD'
    VERBOSE       = 'VERBOSE'
    BREVERSED     = 'BREVERSED'
    OUTPUT        = 'OUTPUT'
    DEP           = 'DEP'

    _default_output = 'cb.svg'
    _ori_lst = ['Vertical', 'Horizontal']
    _tick_lst = ['bottom/left', 'top/right', 'none']
    _fweight = ['ultralight', 'light', 'normal', 'demibold', 'bold', 'extra bold']
    _fontfamily = ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
    _ico = 'bcCbar'
    _the_strings = {"ALGONAME":"Create Colour Scalebar",
                    "VERSION":"Version 4.1",
                    "ERR":"ERROR",
                    "ERR_NOONEBAND":"ERROR: Input is not a one-band raster!",
                    "ERR_DEP":"ERROR: Some needed dependencies are not installed!",
                    "DEP_LST":"numpy, matplotlib, pillow, bs4 and lxml are needed...",
                    "SUCCESS":"Colour bar is created as: ",
                   }
    _pstr = {'THE_LAYER': 'Input one-band raster',
             'ORI': 'Scalebar orientation',
             'TITLE': 'Title',
             'DECI': 'Number of decimals to display',
             'CLENGTH': 'Colour scalebar length',
             'CWIDTH': 'Colour scalebar breadth',
             'DEDGES': 'Draw edge around each colour?',
             'TICKSEP': 'Tick separation',
             'LABEL_ON': 'Location of ticks and labels',
             'LABEL_ALT': 'Additional location of ticks and labels',
             'TITLE_FONT': 'Font name/family for title and labels',
             'FONT_SIZE': 'Title font size',
             'TITLE_COLOR': 'Title colour [k|r|g|b|c|m|y] or "#RRGGBBAA" or colour name',
             'TITLE_WEIGHT': 'Title font weight',
             'TICKFONTSIZE': 'Tick labels font size',
             'TICKLENGTH': 'Ticks length',
             'TICKCOLO': 'Ticks/labels colour [k|r|g|b|c|m|y] or "#RRGGBBAA" or colour name',
             'TWK_REPLACE': 'Replace last tick with end value?',
             'TWK_ADD': 'Add end value to ticks array?',
             'VERBOSE': 'Print information about colour and ticks?',
             'BREVERSED': 'Reverse colour scalebar?',
             'OUTPUT': 'Output SVG file'}

    def __init__(self):
        super().__init__()

    def _define_params(self):
        ''' Define parameters needed. '''
        #
        #       [0] < 100  : "normal" parameter
        # 100 < [0] < 1000 : Advanced Parameter
        #       [0] > 1000 : Output parameter
        self.the_params = {
           self.THE_LAYER:    [1,self._pstr['THE_LAYER'],'RasterLayer',{},False],
           self.ORI:          [11,self._pstr['ORI'],'Enum',
                               {'list':self._ori_lst,'defaultValue':0},True],
           self.CLENGTH:      [12,self._pstr['CLENGTH'],'NumberD',
                               {'defaultValue':10,'minValue':1,'maxValue':100},True],
           self.CWIDTH:       [13,self._pstr['CWIDTH'],'NumberD',
                               {'defaultValue':0.75,'minValue':0.1,'maxValue':20},True],
           self.DEDGES:       [15, self._pstr['DEDGES'],'Bool',{'defaultValue':False},True],
           self.BREVERSED:    [16,self._pstr['BREVERSED'],'Bool',{'defaultValue':False},True],
           self.TITLE:        [20,self._pstr['TITLE'],'String',{'defaultValue':''},True],
           self.TITLE_COLOR:  [21,self._pstr['TITLE_COLOR'],'String',{'defaultValue':'k'},True],
           self.TITLE_FONT:   [24,self._pstr['TITLE_FONT'],'Enum',
                               {'list':self._fontfamily,'defaultValue':1},True],
           self.FONT_SIZE:    [25,self._pstr['FONT_SIZE'],'NumberD',
                               {'defaultValue':28.,'minValue':1.,'maxValue':128.},True],
           self.TITLE_WEIGHT: [26,self._pstr['TITLE_WEIGHT'],'Enum',
                               {'list':self._fweight,'defaultValue':4},True],
           self.DECI:         [30,self._pstr['DECI'],'NumberI',
                               {'defaultValue':2,'minValue':0,'maxValue':12},True],
           self.TICKSEP:      [35,self._pstr['TICKSEP'],'NumberI',
                               {'defaultValue':-5,'minValue':-5,'maxValue':1000000},True],
           self.LABEL_ON:     [40,self._pstr['LABEL_ON'],'Enum',
                               {'list':self._tick_lst,'defaultValue':0},True],
           self.LABEL_ALT:    [41,self._pstr['LABEL_ALT'],'Enum',
                               {'list':self._tick_lst,'defaultValue':2},True],
           self.TICKFONTSIZE: [45,self._pstr['TICKFONTSIZE'],'NumberD',
                               {'defaultValue':14.,'minValue':1.,'maxValue':128.},True],
           self.TICKCOLO:     [46,self._pstr['TICKCOLO'],'String',{'defaultValue':'k'},True],
           self.TICKLENGTH:   [50,self._pstr['TICKLENGTH'],'NumberD',
                               {'defaultValue':8.,'minValue':0.,'maxValue':32.},True],
           self.TWK_REPLACE:  [110, self._pstr['TWK_REPLACE'],'Bool',{'defaultValue':True},False],
           self.TWK_ADD:      [111, self._pstr['TWK_ADD'],'Bool',{'defaultValue':False},False],
           self.VERBOSE:      [120, self._pstr['VERBOSE'],'Bool',{'defaultValue':False},False],
           self.OUTPUT:       [1001,self._pstr['OUTPUT'],'FileDestination',
                               {'FILTER':'*.svg','defaultValue':self._default_output},True]
        }
        self._err_param = {self.DEP: [1,self._the_strings["ERR_DEP"],'String',
                           {'defaultValue':self._the_strings["DEP_LST"]},False]}
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

        # Other variables
        self._error = ''
        self.tmpDir = QgsProcessingUtils.tempFolder()
        self.ori = self._ori_lst[0].lower()
    #-------------------------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        ''' Here is where the processing itself takes place. '''
        #
        if not is_dependencies_satisfied:
            return {}
        #
        tmpf        = str(uuid.uuid4())
        self._error = ''

        the_layer = self.parameterAsRasterLayer(parameters, self.THE_LAYER, context)
        #
        if not check_oneband(the_layer):
            raise QgsProcessingException(self._the_strings["ERR_NOONEBAND"])

        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if (self._default_output in output_file) or (output_file == ''):
            res_file = os.path.splitext(os.path.split(the_layer.source())[1])[0] + '.svg'
            output_file = os.path.join(self.tmpDir, res_file)

        feedback.setProgress(0.)
        labbl = self.parameterAsInt(parameters, self.LABEL_ON, context)
        labtr = self.parameterAsInt(parameters, self.LABEL_ALT, context)
        verbose = self.parameterAsBool(parameters, self.VERBOSE, context)
        kw = {}
        kw['width'] = self.parameterAsDouble(parameters, self.CLENGTH, context)
        kw['height'] = self.parameterAsDouble(parameters, self.CWIDTH, context)
        kw['drawedges'] = self.parameterAsBool(parameters, self.DEDGES, context)
        kw['inverted'] = self.parameterAsBool(parameters, self.BREVERSED, context)
        kw['orientation'] = self._ori_lst[self.parameterAsInt(parameters, self.ORI, context)].lower()
        kw['title'] = self.parameterAsString(parameters, self.TITLE, context).replace('\\n', '\n')
        kw['titlefontname'] = self.parameterAsString(parameters, self.TITLE_FONT, context)
        kw['titlefontsize'] = self.parameterAsDouble(parameters, self.FONT_SIZE, context)
        kw['titlefontweight'] = self.parameterAsString(parameters, self.TITLE_WEIGHT, context)
        kw['titlecolo'] = self.parameterAsString(parameters, self.TITLE_COLOR, context)
        kw['tickfontsize'] = self.parameterAsDouble(parameters, self.TICKFONTSIZE, context)
        kw['tickcolo'] = self.parameterAsString(parameters, self.TICKCOLO, context)
        kw['tickstep'] = self.parameterAsDouble(parameters, self.TICKSEP, context)
        kw['decimal'] = self.parameterAsInt(parameters, self.DECI, context)
        kw['ticklength'] = self.parameterAsDouble(parameters, self.TICKLENGTH, context)
        kw['bottom'] = True if labbl == 0 else False
        kw['left'] = True if labbl == 0 else False
        kw['top'] = True if labtr == 1 else False
        kw['right'] = True if labtr == 1 else False
        kw['tweak_end_replace'] = self.parameterAsBool(parameters, self.TWK_REPLACE, context)
        kw['tweak_end_add'] = self.parameterAsBool(parameters, self.TWK_ADD, context)
        kw['verbose'] = verbose

        if verbose:
            feedback.pushInfo('\n'.join('%s: %s' % (k, str(w)) for k, w in kw.items()))
            feedback.pushInfo('\n'+'='*40+'\n\n')

        feedback.setProgress(10.)
        mycb = drawCBar(the_layer, svg_file=output_file, noQML=True, **kw)

        feedback.setProgress(20.)
        if not mycb.createCBar():
            self._error = mycb.err
        feedback.setProgress(95.)

        if verbose:
            feedback.pushInfo(mycb.L_Verbose+'\n')
        mycb.close()
        if self._error != '':
            feedback.reportError(self._error+'\n', True)
        else:
            feedback.pushWarning('\n\n'+self._the_strings["SUCCESS"]+output_file+'\n\n')
        #
        feedback.setProgress(100.)
        return {self.OUTPUT:output_file}
    #-------------------------------------------------------------------------------------

    def get_error(self):
        ''' Return the error value. '''
        #
        return self.tr(self._error)
    #-------------------------------------------------------------------------------------

    def icon(self):
        ''' Returns a QIcon for the algorithm. '''
        #
        return QIcon(os.path.join(os.path.join(plugin_path, 'res', self._ico+'.svg')))
    #-------------------------------------------------------------------------------------

    def svgIconPath(self):
        ''' Returns a path to an SVG version of the algorithm's icon. '''
        #
        return QIcon(os.path.join(os.path.join(plugin_path, 'res', self._ico+'.svg')))
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
        return 'bcCBar3'
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
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'composer'
    #-------------------------------------------------------------------------------------

    def tr(self, string):
        ''' Not implemented. '''
        #
        return string
    #-------------------------------------------------------------------------------------

    def createInstance(self):
        ''' Creates a new instance of the algorithm class. '''
        #
        return bcCBarAlgorithm()
    #-------------------------------------------------------------------------------------
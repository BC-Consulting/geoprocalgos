# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bcCBar3
                           A QGIS Processing algorithm
                      Create a colour scalebar for Composer

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
                       QgsProcessingUtils,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterDefinition,
                       QgsMapLayer)

from .bcCBar3 import bcColorBar

# Check for dependencies
from .bcCBar3 import is_bs4_available, is_mpl_available
is_dependencies_satisfied = is_bs4_available and is_mpl_available

#-----------------------------------------------------------------------------------------
FlagsAdv = QgsProcessingParameterDefinition.FlagAdvanced
plugin_path = os.path.join(os.path.split(os.path.dirname(__file__))[0], 'geoprocAlgos')

the_url = 'http://www.geoproc.com/free/bccbar3.htm'
help_string = """
<i>Generate a colour scalebar from a one-band raster for use in Composer</i>
<b>Paramaters needed to draw the scalebar are</b>:<br/>
<b>Required</b>
Input: currently selected raster in QGIS legend. A qml file will automatically be created.
<br/><b>Optional</b>
Scalebar orientation: "vertical"* or "horizontal"
Number of decimals to display in tick labels (default: 2)
Title of the colour scalebar. Use ÿ (ASCII 255) as multilines marker.
Sub-title of the colour scalebar (single line). Generally units of the raster.
Ratio width of the colour scalebar relative to full length (0.1)
Tick separation: every 'ticksep' is shown (default: 1 [>= 1])
Offset to arrive at nice numbers for ticks labelling (default: 0. [-100., 100.])
Label both sides of the colour scalebar or not. False*
Or which side to label: 'none', 'both', 'top', 'bottom'*, 'right'*, 'left'.
Ticks label font size relative to plot area. Default 4, [.2, 10.]
Title font size relative to ticks label font size (+2)* [-10.,10.]
Sub-title font size relative to ticks label font size (+1)*
Colour scalebar frame line width (default 1.0 [0.0, 5.0])
Colour dividers line width, between colours (default 0.0 [0., 2.5])
Title colour ('black'*)
Sub-title colour ('black'*)
Frame colour ('black'*)
Divider colour ('black'*)
The scalebar can be reversed. False*
A png file can be created in addition to the svg file. False*
Additional parameters can be defined. See home page for more details.<br/>
Ouptut: the name of the svg file representing the generated colour scalebar.<br/>
*: default<br/><br/>
-------------------------------------------------------------------
One-band-rasters saved with QGIS V3.x are the only ones accepted.
Colour interpolation can be: LINEAR, EXACT, DISCRETE or PALETTED.
Colour mode can be: Continuous, Equal Interval or Quantile.<br/>
Title and sub-title accept text formatted in Maptplotlib mathtext.
-------------------------------------------------------------------
"""
svg_note = """<p>"It is known that some vector graphics viewers (svg and pdf) 
renders white gaps between segments of the colorbar. This is due to bugs in the viewers, 
not Matplotlib."<br/>\n<em>source: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.
colorbar.html</em></p>\n"""
the_tags = ['colour','scale','bar','scalebar','raster','1-band','one-band','oneband',
            'composer','svg','png','print','legend']
#-----------------------------------------------------------------------------------------

class bcCBarAlgorithm(QgsProcessingAlgorithm):
    ''' Processing wrapper for the colour scale bar algorithm. '''
    #
    # Parameters used for drawing the colour scale bar
    THE_LAYER     = 'THE_LAYER'
    ORI           = 'ORI'
    TITLE         = 'TITLE'
    UNITS         = 'UNITS'
    DECI          = 'DECI'
    CBWH          = 'CBWH'
    TICKSEP       = 'TICKSEP'
    OFFSET        = 'OFFSET'
    LABEL_BOTH    = 'LABEL_BOTH'
    LABEL_ON      = 'LABEL_ON'
    FONT_SIZE     = 'FONT_SIZE'
    TFONT         = 'TFONT'
    UFONT         = 'UFONT'
    BORDER_LW     = 'BORDER_LW'
    DIVIDER_LW    = 'DIVIDER_LW'
    TITLE_COLOR   = 'TITLE_COLOR'
    UNITS_COLOR   = 'UNITS_COLOR'
    BORDER_COLOR  = 'BORDER_COLOR'
    DIVIDER_COLOR = 'DIVIDER_COLOR'
    BREVERSED     = 'BREVERSED'
    WITH_PNG      = 'WITH_PNG'
    XTRA_PARAM    = 'XTRA_PARAM'
    OUTPUT        = 'OUTPUT'
    DEP           = 'DEP'

    _default_output = 'cb.svg'
    _ori_lst = ['Vertical', 'Horizontal']
    _tick_lst = ['right', 'left', 'top', 'bottom', 'none']

    _the_strings = {"ERR":"ERROR",
                    "ERR_NOONEBAND":"ERROR: Input is not a one-band raster!",
                    "ERR_NOSAVEQML":"ERROR: Cannot save .qml file in temp directory!",
                    "ERR_NOSIDECAR":" And, no qml side-car found.",
                    "ERR_NOQML":"ERROR: Input file is neither a raster neither a .qml!",
                    "ERR_MPL":"ERROR: matplotlib and numpy are needed!",
                    "ERR_BS4":"ERROR: BeautifulSoup4 and lxml are needed!",
                    "ERR_DEP":"ERROR: Needed dependencies are not installed!",
                    "DEP_LST":"numpy, matplotlib, BeautifulSoup4 and lxml are needed...",
                    "CREATE_CS":"Create Colour Scalebar",
                    "SOURCE":"Source",
                    "RESULT":"Result: colour scalebar",
                    "PARAMS":"Parameters Used",
                    "COPYPASTE":"(copy and paste into Composer image source box)",
                    "SUFFIX":'''<h5>Suffix explanation:</h5>
                              <ul>
                              <li>H or V: for horizontal and vertical respectively</li>
                              <li>number: Colour interpolation: 
                                 0: discrete, 1: linear, 2: exact and 3: paletted</li>
                             <li>number: Colour mode: 1: Continuous, 2: Equal interval,
                                 3: Quantile</li>
                             <li>T or F: annotate both sides of the scalebar (T)
                                 or not (F)</li>
                             <li>letter: tick position: one of n (none), l (left), 
                                 r (right), t(top) or b (bottom)</li>
                             </ul>
                             '''}

    _pstr = ['Input one-band raster', 'Scalebar orientation', 'Title', 'Sub-title',
            'Number of decimals to display', 'Colour scalebar ratio: width/length',
            'Tick separation', 'Ticks offset to arrive at nice numbers', 
            'Ticks on both side?', 'Ticks position', 'Ticks font size (relative)', 
            'Title font size (relative to ticks font)', 
            'Sub-title font size (relative to ticks font)',
            'Colour scalebar frame thickness (points)',
            'Colours divider thickness (points)',
            'Title colour (r,g,b,a) [0., 1.] or colour name',
            'Sub-title colour (r,g,b,a) [0., 1.] or colour name',
            'Frame/labels colour (r,g,b,a) [0., 1.] or colour name',
            'Dividers colour (r,g,b,a) [0., 1.] or colour name',
            'Reverse colour scalebar?', 'Output a png file as well? (SVG by default)',
            'Additional parameters. See home page for help.',
            'Result file', 'HTML files (*.html)', 'All files (*.*)']

    def __init__(self):
        super().__init__()

    def _define_params(self):
        ''' Define parameters needed. '''
        #
        #       [0] < 100  : "normal" parameter
        # 100 < [0] < 1000 : Advanced Parameter
        #       [0] > 1000 : Output parameter
        self.the_params = {
           self.THE_LAYER:    [1,self._pstr[0],'RasterLayer',{},False],
           self.ORI:          [20,self._pstr[1],'Enum',
                               {'list':self._ori_lst,'defaultValue':0},True],
           self.TITLE:        [30,self._pstr[2],'String',{'defaultValue':''},True],
           self.UNITS:        [40,self._pstr[3],'String',{'defaultValue':''},True],
           self.DECI:         [50,self._pstr[4],'NumberI',
                               {'defaultValue':2,'minValue':0,'maxValue':12},True],
           self.TICKSEP:      [60,self._pstr[6],'NumberI',
                               {'defaultValue':1,'minValue':1,'maxValue':1000000},True],
           self.CBWH:         [101,self._pstr[5],'NumberD',
                               {'defaultValue':0.1,'minValue':0.001,'maxValue':1.0},True],
           self.OFFSET:       [110,self._pstr[7],'NumberD',
                               {'defaultValue':0.,'minValue':-100.,'maxValue':100.},True],
           self.LABEL_BOTH:   [120,self._pstr[8],'Bool',{'defaultValue':False},True],
           self.LABEL_ON:     [130,self._pstr[9],'Enum',
                               {'list':self._tick_lst,'defaultValue':0},True],
           self.FONT_SIZE:    [140,self._pstr[10],'NumberD',
                               {'defaultValue':4.,'minValue':0.2,'maxValue':100.},True],
           self.TFONT:        [150,self._pstr[11],'NumberD',
                               {'defaultValue':2.,'minValue':-10.,'maxValue':10.},True],
           self.UFONT:        [160,self._pstr[12],'NumberD',
                               {'defaultValue':1.,'minValue':-10.,'maxValue':10.},True],
           self.BORDER_LW:    [170,self._pstr[13],'NumberD',
                               {'defaultValue':1.,'minValue':0.,'maxValue':5.},True],
           self.DIVIDER_LW:   [180,self._pstr[14],'NumberD',
                               {'defaultValue':0.,'minValue':0.,'maxValue':2.5},True],
           self.TITLE_COLOR:  [190,self._pstr[15],'String',{'defaultValue':'black'},True],
           self.UNITS_COLOR:  [200,self._pstr[16],'String',{'defaultValue':'black'},True],
           self.BORDER_COLOR: [210,self._pstr[17],'String',{'defaultValue':'black'},True],
           self.DIVIDER_COLOR:[220,self._pstr[18],'String',{'defaultValue':'black'},True],
           self.BREVERSED:    [230,self._pstr[19],'Bool',{'defaultValue':False},True],
           self.WITH_PNG:     [240,self._pstr[20],'Bool',{'defaultValue':False},True],
           self.XTRA_PARAM:   [250,self._pstr[21],'String',{'defaultValue':''},True],
           self.OUTPUT:       [1001,self._pstr[22],'FileDestination',
                             {'FILTER':self._pstr[23],'defaultValue':self._default_output}
                             ,True]
        }
    #-------------------------------------------------------------------------------------

    def _set_param(self, param):
        ''' Set parameter. '''
        #
        arg = self.the_params[param]
        what = arg[2]
        optional = arg[4]
        the_str = arg[1]
        qparam = None
        #
        if what == 'RasterLayer':
            qparam = QgsProcessingParameterRasterLayer(
                    param,
                    self.tr(the_str),
                    optional = optional
                )
        elif what == 'File':
            qparam = QgsProcessingParameterFile(
                    param,
                    self.tr(the_str),
                    extension = arg[3]['ext'],
                    optional = optional
                )
        elif what == 'Enum':
            qparam = QgsProcessingParameterEnum(
                    param,
                    self.tr(the_str),
                    [self.tr(s) for s in arg[3]['list']],
                    defaultValue = arg[3]['defaultValue'],
                    optional = optional
                )
        elif what == 'String':
            qparam = QgsProcessingParameterString(
                    param,
                    self.tr(the_str),
                    defaultValue = arg[3]['defaultValue'],
                    optional = optional
                )
        elif what == 'NumberD':
            qparam = QgsProcessingParameterNumber(
                    param,
                    self.tr(the_str),
                    type = QgsProcessingParameterNumber.Double,
                    defaultValue = arg[3]['defaultValue'],
                    minValue = arg[3]['minValue'],
                    maxValue = arg[3]['maxValue'],
                    optional = optional
                )                
        elif what == 'NumberI':
            qparam = QgsProcessingParameterNumber(
                    param,
                    self.tr(the_str),
                    type = QgsProcessingParameterNumber.Integer,
                    defaultValue = arg[3]['defaultValue'],
                    minValue = arg[3]['minValue'],
                    maxValue = arg[3]['maxValue'],
                    optional = optional
                )                
        elif what == 'Bool':
            qparam = QgsProcessingParameterBoolean(
                    param,
                    self.tr(the_str),
                    defaultValue = arg[3]['defaultValue'],
                    optional = optional
                )                
        elif what == 'FileDestination':
            qparam = QgsProcessingParameterFileDestination(
                    param,
                    self.tr(the_str),
                    defaultValue = arg[3]['defaultValue'],
                    fileFilter = arg[3]['FILTER'],
                    optional = optional
                )
        #
        if qparam != None:
            if arg[0] < 100:
                self.addParameter(qparam)
            elif arg[0] < 1000:
                qparam.setFlags(qparam.flags() | FlagsAdv)
                self.addParameter((qparam))
            else:
                self.addParameter(qparam, True)
    #-------------------------------------------------------------------------------------

    def _save_qml(self, theLayer):
        ''' Save the layer style to a qml file. '''
        #
        theFile = theLayer.name().split("|")[0] + ".qml"
        tempname = os.path.join(self.tmpDir, theFile)
        _, flg = theLayer.saveNamedStyle( tempname )
        if flg:
            return [True, tempname]
        else:
            return [False, self._the_strings["ERR_NOSAVEQML"]]
    #-------------------------------------------------------------------------------------

    def _check_color(self, col):
        ''' Check that col can be interpreted as a colour. '''
        #
        if type(col) == list or type(col) == tuple:
            if len(col) > 2 and len(col) < 5:
                try:
                    for i in col:
                        _ = float(i)
                except:
                    return 'black'
            else:
                return 'black'
        elif type(col) != str:
            return 'black'
        #
        return col
    #-------------------------------------------------------------------------------------

    def _check_oneband(self, F):
        ''' Check that the given file is a one-band raster. '''
        #
        if F is None or F.type() != QgsMapLayer.RasterLayer:
            return False
        elif F.rasterType() > 0:
            return False
        else:
            return True
    #-------------------------------------------------------------------------------------

    def _check_sidecar(self, the_layer):
        ''' Check is a qml side-car exist for the raster. '''
        #
        qml = os.path.splitext(the_layer.source())[0] + '.qml'
        if os.path.exists(qml):
            return qml
        else:
            return False
    #-------------------------------------------------------------------------------------

    def _continue_proc(self, mycb, ori, labboth, output_file):
        ''' Continue processing. '''
        #
        if self.xtrap != '':
            mycb.set_extras(self.xtrap)
        #
        vh = '_' + self._ori_lst[ori][0] + str(mycb.nMode) + str(mycb.cm)
        self.dico['label_on'] = mycb.Labelson
        output_file = output_file + vh + str(labboth)[0] + mycb.Labelson[0] + '.svg'
        mycb.set_out_file(output_file)
        #
        if mycb.draw_cb():
            if not mycb.save_cb():
                self._error = mycb.get_error()
        else:
            self._error = mycb.get_error()
        #
        mycb.close()
        return output_file
    #-------------------------------------------------------------------------------------

    def _create_HTML(self, svg_file, the_cb = None):
        ''' Generate an output html file showing the create colour bar (svg). '''
        #
        # Internationalisation
        for k in the_cb.xtra:
            the_cb.xtra[k] = self.tr(the_cb.xtra[k])
        the_cb.the_strings["EM"] = self.tr(the_cb.the_strings["EM"])
        the_cb.the_strings["XTRA_PARAMS"] = self.tr(the_cb.the_strings["XTRA_PARAMS"])
        #-----------------------------------------------------------------------------
        #
        outputFile = os.path.splitext(svg_file)[0] + "_bcCBar-results.html"
        svg_htm = os.path.split(svg_file)[1]
        #
        if self.ori == 'vertical':
            wh = 'height:800px;'
            wd = 'width:300px;'
        else:
            wh = 'width:900px;'
            wd = wh
        #
        with codecs.open(outputFile, 'w', encoding='utf-8') as f:
            f.write('<html>\n<head>\n')
            f.write('<meta http-equiv="Content-Type" content="text/html;') 
            f.write(' charset=utf-8" />\n</head>\n<body>\n')
            if self._error != '':
                f.write('<h1>%s</h1>\n' % self.tr(self._the_strings["ERR"]))
                f.write('<p style="color:red;">%s</p>\n' % self.tr(self._error))
            #
            else:
                f.write('<h1>%s</h1>\n' % self.tr(self._the_strings["RESULT"]))
                if self.dico['with_png']:
                    png = svg_htm[:-3] + 'png'
                    f.write('<table width="940" align="center" cellspacing="10">\n')
                    if self.dico['ori'] == 'vertical':
                        f.write(' <tr>\n  <td widh="50%">\n   <h3>SVG</h3>\n')
                        f.write('   <div style="%s margin:auto;">\n' % wd)
                        f.write('   <iframe style="border:0px; %s" src="%s"></iframe>\n'% 
                                (wh, svg_htm))
                        f.write('   </div>\n')
                        f.write('  </td>\n  <td width="50%">\n   <h3>PNG</h3>\n')
                        f.write('   <img src="%s" %s/>\n'% (png, wh))
                    else:
                        f.write(' <tr>\n  <td>\n   <h3>SVG</h3>\n')
                        f.write('   <div style="%s margin:auto;">\n' % wd)
                        f.write('   <iframe style="border:0px; %s" src="%s"></iframe>\n'% 
                                (wh, svg_htm))
                        f.write('   </div>\n')
                        f.write('  </td>\n </tr>\n <tr>\n  <td>\n   <h3>PNG</h3>\n')
                        f.write('   <img src="%s" %s/>\n'% (png, wh))
                    f.write('  </td>\n </tr>\n</table>\n')
                else:
                    f.write('<div style="%s margin:auto;">\n' % wd)
                    f.write('<iframe style="border:0px; %s" src="%s"></iframe>\n'% 
                            (wh, svg_htm))
                    f.write('</div>\n')
                #
                f.write('<p align="center">%s (svg): <a href="%s">%s</a> %s</p>\n' % 
                        (self.tr(self._the_strings["SOURCE"]), svg_file, svg_file,
                         self.tr(self._the_strings["COPYPASTE"])))
                if self.dico['with_png']:
                    f.write('<p align="center">%s (png): <a href="%s">%s</a></p>\n' % 
                            (self.tr(self._the_strings["SOURCE"]), png, png))
                f.write('<p align="center"><a href="file:///%s"><em>%s</em></a></p>\n' % 
                        (os.path.split(svg_file)[0], os.path.split(svg_file)[0]))
                #
                f.write(self.tr(self._the_strings['SUFFIX']))
                #
                f.write('<hr/>\n<h2>%s</h2>\n' % self.tr(self._the_strings["PARAMS"]))
                f.write(the_cb.get_params_used(self.the_layer.source(), self.the_params))
                f.write('<hr/>\n')
                f.write(self.tr(svg_note))
            f.write('</body>\n</html>\n')
        #
        return outputFile
    #-------------------------------------------------------------------------------------

    def initAlgorithm(self, config):
        ''' Here we define the inputs and output of the algorithm. '''
        #
        if is_dependencies_satisfied:
            # Prepare all parameters needed for plotting the colour bar
            self._define_params()
            for param in sorted(self.the_params, key=self.the_params.__getitem__):
                self._set_param(param)

            # Other variables
            self._error = ''
            self.tmpDir = QgsProcessingUtils.tempFolder()
            self.ori = self._ori_lst[0].lower()
        else:
            qparam = QgsProcessingParameterString(
                    self.DEP,
                    self.tr(self._the_strings["ERR_DEP"]),
                    defaultValue = self.tr(self._the_strings["DEP_LST"]),
                    optional = False
                )
            self.addParameter(qparam)
    #-------------------------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        ''' Here is where the processing itself takes place. '''
        #
        if not is_dependencies_satisfied:
            return {}
        #
        tmpf        = str(uuid.uuid4())
        res_file    = os.path.join(self.tmpDir, tmpf + '.htm')
        b_with_qml  = False
        self._error = ''

        self.the_layer = self.parameterAsRasterLayer(parameters, self.THE_LAYER, context)
        #
        if not self._check_oneband(self.the_layer):
            self._error = self._the_strings["ERR_NOONEBAND"]
            fil = self._create_HTML(res_file)
            return {self.OUTPUT:fil}

        bOk, qml_file = self._save_qml(self.the_layer)
        if not bOk:
            self._error = qml_file
            fil = self._create_HTML(res_file)
            return {self.OUTPUT:fil}

        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if (self._default_output in output_file) or (output_file == ''):
            res_file = os.path.splitext(os.path.split(self.the_layer.source())[1])[0]
            output_file = os.path.join(self.tmpDir, res_file)
        else:
            output_file = os.path.splitext(output_file)[0]

        ori           = self.parameterAsInt(parameters, self.ORI, context)
        self.ori      = self._ori_lst[ori].lower()
        label_on      = self.parameterAsInt(parameters, self.LABEL_ON, context)
        labelon       = self._tick_lst[label_on]
        divider_color = self.parameterAsString(parameters, self.DIVIDER_COLOR, context)
        border_color  = self.parameterAsString(parameters, self.BORDER_COLOR, context)
        title_color   = self.parameterAsString(parameters, self.TITLE_COLOR, context)
        units_color   = self.parameterAsString(parameters, self.UNITS_COLOR, context)
        labboth       = self.parameterAsBool(parameters,   self.LABEL_BOTH, context)
        the_titre     = self.parameterAsString(parameters, self.TITLE, context)
        the_titre = the_titre.replace('\\n', 'ÿ')

        self.dico = {'ori': self.ori,
                    'deci': self.parameterAsDouble(parameters, self.DECI, context),
                   'title': the_titre,
                   'units': self.parameterAsString(parameters, self.UNITS, context),
                    'cbwh': self.parameterAsDouble(parameters, self.CBWH, context),
                 'ticksep': self.parameterAsDouble(parameters, self.TICKSEP, context),
                  'offset': self.parameterAsDouble(parameters, self.OFFSET, context),
              'label_both': labboth,
                'label_on': labelon,
               'font_size': self.parameterAsDouble(parameters, self.FONT_SIZE, context),
                   'tfont': self.parameterAsDouble(parameters, self.TFONT, context),
                   'ufont': self.parameterAsDouble(parameters, self.UFONT, context),
                'with_png': self.parameterAsBool(parameters,   self.WITH_PNG, context),
               'border_lw': self.parameterAsDouble(parameters, self.BORDER_LW, context),
              'divider_lw': self.parameterAsDouble(parameters, self.DIVIDER_LW, context),
           'divider_color': self._check_color(divider_color),
            'border_color': self._check_color(border_color),
             'title_color': self._check_color(title_color),
             'units_color': self._check_color(units_color),
               'breversed': self.parameterAsBool(parameters, self.BREVERSED, context)
        }

        self.xtrap = self.parameterAsString(parameters, self.XTRA_PARAM, context)

        mycb = bcColorBar(qml_file, '', **self.dico)
        if mycb.get_init_state():
            output_file = self._continue_proc(mycb, ori, labboth, output_file)
        else:
            self._error = mycb.get_error()
            if self._error == mycb.the_strings["E_NOSTYLE"]:
                # This is one band raster but not styled (could be straight from file)
                # If yes, look for the qml side-car. If not found, abort
                qml_file = self._check_sidecar(self.the_layer)
                if qml_file:
                    self._error = ''
                    b_with_qml = True
                    mycb = bcColorBar(qml_file, '', **self.dico)
                    if mycb.get_init_state():
                        output_file = self._continue_proc(mycb, ori, labboth, output_file)
                    else:
                        self._error = mycb.get_error()
                else:
                    # Not properly styled and no qml side-car
                    self._error = mycb.get_error() + self._the_strings["ERR_NOSIDECAR"]
        #
        if not b_with_qml:
            try:
                os.remove(qml_file)
            except:
                pass

        if self._error != '':
            fil = self._create_HTML(res_file)
        else:
            fil = self._create_HTML(output_file, mycb)
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
        return QIcon(os.path.join(plugin_path, 'res', 'bcCBar.svg'))
    #-------------------------------------------------------------------------------------

    def svgIconPath(self):
        ''' Returns a path to an SVG version of the algorithm's icon. '''
        #
        return os.path.join(plugin_path, 'res', 'bcCBar.svg')
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
        return self.tr(self._the_strings["CREATE_CS"])
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
        ''' No translation of strings. '''
        #
        return string
    #-------------------------------------------------------------------------------------

    def createInstance(self):
        ''' Creates a new instance of the algorithm class. '''
        #
        return bcCBarAlgorithm()
    #-------------------------------------------------------------------------------------
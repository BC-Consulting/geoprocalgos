# -*- coding: utf-8 -*-
"""
/***************************************************************************
        begin                : 2022-04-10
        copyright            : (C) 2019-2023 by GeoProc.com
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

  drawCBar
      draw a colour scale bar and save it to SVG

  readQML
      read a QGIS V3.x .qml file

  BCgetSymbology
      get raster info and colourbar from QGIS layer

WARNING: code formatting does not follow pycodestyle recommendations
"""

import os
import sys
# import shutil

#   Test for dependencies -------------------------------------
is_mpl_available = False
is_bs4_available = False
try:
    import matplotlib as mpl
    import numpy as np
    import matplotlib.pyplot as plt
    is_mpl_available = True
except ImportError:
    try:
        os.system('"' + os.path.join(sys.prefix, 'scripts', 'pip.exe') + '" install matplotlib')
    finally:
        import matplotlib as mpl
        is_mpl_available = True

try:
    from bs4 import BeautifulSoup, __version__ as bs4_version
    is_bs4_available = True
except ImportError:
    try:
        os.system('"' + os.path.join(sys.prefix, 'scripts', 'pip.exe') + '" install lxml')
        os.system('"' + os.path.join(sys.prefix, 'scripts', 'pip.exe') + '" install bs4')
    finally:
        from bs4 import BeautifulSoup, __version__ as bs4_version
        is_bs4_available = True

try:
    from .svg_manip import bc_svg
    from .utils import get_dom
except:
    from svg_manip import bc_svg
    from utils import get_dom

try:
    from qgis.core import (
        QgsRasterLayer,
        QgsProject,
        QgsPointXY,
        QgsRaster,
        QgsRasterShader,
        QgsColorRampShader,
        QgsSingleBandPseudoColorRenderer,
        QgsSingleBandColorDataRenderer,
        QgsSingleBandGrayRenderer,
    )
    from qgis.PyQt.QtGui import QColor
    is_QGIS_available = True
except:
    is_QGIS_available = False

if is_mpl_available:
    plt.rc('text', usetex=False)
    mv = mpl.__version__.split('.')
    if int(mv[0]) < 3 and int(mv[1]) < 5:
        is_mpl_available = False

__version__ = "3.3.1"

#==========================================================================
print('cbar version:', __version__)
if is_mpl_available:
    print('    is_mpl_available: %s [Version: %s]' % (str(is_mpl_available), str(mpl.__version__)))
else:
    print('    is_mpl_available: False')
if is_bs4_available:
    print('    is_bs4_available %s [Version: %s]' % (str(is_bs4_available), str(bs4_version)))
else:
    print('    is_bs4_available: False')
print('    is_QGIS_available:', is_QGIS_available)
#==========================================================================

if not is_QGIS_available:
    cbar_usage = '''<h1>Usage</h1>
<p><b>QGIS V3.x qml</b> [required]: Click 'Change' to select the QML style file to draw colour bar from.<br />
<b>Output cbar svg</b> [optional]: Click 'Change' to define the path and name of the SVG colour bar result.<br />
   &nbsp; &nbsp; &nbsp; If SVG is not defined the QML file name is used to set the SVG name.</p></p>
<hr />
<h2><font color="#600">Optional parameters:-</font></h2>
<h3><font color="#006">Colour bar:</font></h3>
<b>Length</b>: [float] colour bar height (0.75)<br />
<b>width</b>: [float] colour bar width (15)<br />
<p><b>orientation</b>: [str] ('horizontal'* | 'vertical'): colour bar orientation<br />
<!-- <b>spacing</b>: [str] ('uniform'* | 'proportional'): colour boxes lengths<br /> -->
<b>Draw colour edges</b>: [bool] draw box around each colour (False)<br />
<b>Reverse colour bar</b>: [bool] reverse the direction of the colour bar (False)</p>
<hr />
<h3><font color="#006">Title:</font></h3>
<p><b>Title</b>: [str] colour bar label ('')<br />
   &nbsp; &nbsp; &nbsp; (use \\n for line break. Use $...$ TeX notation for math expressions)<br />
<b>Title font name</b>: [str] font name/family: FONTNAME or one of {serif, sans-serif*, cursive, fantasy, monospace}<br />
<b>Title font size</b>: [str|int] title font size (28*) number or one of:<br />
   &nbsp; &nbsp; &nbsp; {xx-small, x-small, small, medium, large, x-large, xx-large}<br />
<b>Title font weight</b>: [str|int] title font weight: number [0, 1000] or one of:<br />
   &nbsp; &nbsp; &nbsp; {ultralight, light, normal, demibold, bold*, extra bold}<br />
<b>Title colour</b>: [str] title font colour: [k*|r|g|b|c|m|y] or "#RRGGBBAA" or colour name</p>
<hr />
<h3><font color="#006">Ticks and labels parameters:</font></h3>
<p><b>Tick label font size</b>: [str|int] tick label font size (16) or one of the above<br />
<b>Tick label colour</b>: [str] ticks/labels font colour: [k*|r|g|b|c|m|y] or "#RRGGBBAA" or colour name<br />
<b>tick separation</b>: [+int] show label every `tick separation` ticks (-5)<br />
 &nbsp; &nbsp; &nbsp; can also be:<br />
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; -1: to set tickstep to 1 or 4 depending on colourbar length<br />
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; -3: to set 3 (min, half, max) ticks<br />
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; -5*: to set 3 (min, half, max) or 5 ticks (min, 1/4, 1/2, 3/4, max)<br />
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; depending on number of colours<br />
<b>Decimal places</b>: [positive int] number of decimal places for tick labels (3)<br />
<b>Tick length</b>: [float] tick length (8)</p>
<h4><font color="#006">Ticks/Labels position:</font></h4>
<p><b>top</b>: [bool] show thicks/label on top of horizontal colour bar (False)<br />
<b>bottom</b>: [bool] show thicks/label at bottom of horizontal colour bar (True)<br />
<b>left</b>: [bool] show thicks/label on left of vertical colour bar (True)<br />
<b>right</b>: [bool] show thicks/label on right of vertical colour bar (False)</p><hr />
<h3><font color="#006">Tweak ticks:</font></h3>
<p><b>None</b>: do not show any tick/label<br />
<b>Replace last tick</b>: [bool] replace last tick with end value (True)<br />
<b>Add end tick</b>: [bool] add end value to ticks array (False)</p>
<h3><font color="#006">Debug parameter:</font></h3>
<p><b>Verbose</b>: [bool] (False) print information about the colours and ticks</p>
<p>&nbsp;</p>
<p>*: default value</p>
'''
else:
    cbar_usage = """
<i>Generate a colour scalebar (cbar) from a one-band raster for use in Composer</i>
<b><font color="#f00">Only works for the "Singleband pseudocolour" renderer</font></b>
Paramaters needed to draw the scalebar are:
<b>Required</b>
* <b>Input</b>: currently selected raster in QGIS legend. A qml file will automatically be created.<br/>

<b>Optional</b>
* <b>Colour bar orientation</b>: orientation of the cbar: either 'Vertical' or 'Horizontal'*.
* <b>Colour bar length</b>: [float] length of the cbar in cm (10*).
* <b>Colour bar breadth</b>: [float] width of the cbar in cm (0.75*).
* <b>Draw edge around each colour?</b> True/False*.
* <b>Reverse colour bar?</b> True/False*.<br/> &nbsp; &nbsp; &nbsp; Default is minimum at bottom/left, maximum at top/right.
* <b>Title</b> of the cbar [str]. Use '\\n' as multilines marker.
* <b>Title Colour</b>: [str] one of: [k*|r|g|b|c|m|y] or "#RRGGBBAA" or colour name.
* <b>Font family for title and labels</b>: [str] one of:<br/> &nbsp; &nbsp; &nbsp; {serif, sans-serif*, cursive, fantasy, monospace}.
* <b>Title font size</b>: [float] (28*).
* <b>Title font weight</b>: [str] one of:<br/> &nbsp; &nbsp; &nbsp; {ultralight, light, normal, demibold, bold*, extra bold}.
* <b>Number of decimals to display</b> in tick labels [int] (2*)
* <b>Tick separation</b>: every 'ticksep' is shown [int] (-5*)<br/> &nbsp; &nbsp; &nbsp; can be:
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; -1: to set tickstep to 1 or 4 depending on colourbar length
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; -3: to set 3 (min, half, max) ticks
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; -5: to set 3 (min, half, max) or 5 ticks (min, 1/4, 1/2, 3/4, max)
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; depending on number of colours
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; int > 0 to set tickstep to custom spacing.
* <b>Location of ticks ans labels</b> [str] one of:
 &nbsp; &nbsp; &nbsp; <i>bottom/left</i>: below cbar if orientation is horizontal,<br/> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; left of cbar if orientation is vertical;
 &nbsp; &nbsp; &nbsp; <i>top/right</i>: above cbar if orientation is horizontal,<br/> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; right of cbar if orientation is vertical;
 &nbsp; &nbsp; &nbsp; <i>none</i>: do not show ticks and labels.
 * <b>Additional location of ticks and labels</b>: [str] Add opposite ticks and labels (none*). One of:
 &nbsp; &nbsp; &nbsp; <i>bottom/left</i>: below cbar if orientation is horizontal,<br/> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; left of cbar if orientation is vertical;
 &nbsp; &nbsp; &nbsp; <i>top/right</i>: above cbar if orientation is horizontal,<br/> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; right of cbar if orientation is vertical;
 &nbsp; &nbsp; &nbsp; <i>none</i>: do not show ticks and labels.
* <b>Tick labels font size</b>: [float] labels size (14*).
* <b>Ticks/labels colour</b>: [str] one of: [k|r|g|b|c|m|y] or "#RRGGBBAA" or colour name. Default: #666666
* <b>Ticks length</b>: [float] length of the ticks in pixels.
<b>Advances parameters (tweaking)</b>
* <b>Replace last tick with end value?</b>: if end tick label collides with tick label before it set it True*. Otherwise False.
* <b>Add end value to ticks array?</b>: if last tick label is not the end value set it True. Otherwise False*.
* <b>Print information about colour and ticks?</b>: False*. Set it True for debug purposes only.<br/>

* <b>Output SVG file</b>: the name of the svg (and png) file(s) representing the generated colour scalebar. If left blank temporary SVG/PNG files are created in /temp/ folder.
---
(*): default<br/><br/>

-------------------------------------------------------------------
One-band-rasters saved with QGIS V3.x are the only ones accepted.<br/>Support for "Singleband pseudocolour" renderer only, no other renderer supported.<br/>Colour interpolation can be: LINEAR, EXACT, DISCRETE or PALETTED.<br/>Colour mode can be: Continuous, Equal Interval or Quantile.
Title and sub-title accept text formatted in Maptplotlib mathtext.
-------------------------------------------------------------------
"""
# =========================================================================================


def isfloat(value):
    ''' Test if value can be a float. '''
    #
    try:
        float(value)
        return True
    except ValueError:
        return False
# =========================================================================================


def tofloat(value):
    '''Convert string value to float if possible.
       Returns numpy.nan otherwise.
    '''
    #
    if isfloat(value):
        return float(value)
    v = value.replace(' ', '')
    if isfloat(v):
        return float(v)
    ic = v.find(',')
    ip = v.find('.')
    if ip > ic:
        # 1,234,567.99
        v = v.replace(',', '')
        if isfloat(v):
            return float(v)
    elif ip < ic:
        # 1.234.567,99
        v = v.replace('.', '')
        v = v.replace(',', '.')
        if isfloat(v):
            return float(v)
    # else: ip = ic = -1
    return np.nan
# =========================================================================================


class myFeedBack():
    '''Give user fedback.'''

    def __init__(self):
        pass

    def pushInfo(self, ss):
        print(ss)
# =========================================================================================


class errorObject():
    """Store current error."""
    #
    the_strings = {"E_BADFIL": "ERROR: Wrong input file (expected a QGIS V3.x .QML file)!",
                   "E_BADQML": "ERROR: Wrong QML version %d. Expected 3!",
                   "E_NOONEBAND": "ERROR: Not a one-band raster!",
                   "E_NOCOL": "ERROR: Not enough colours. Minimum 2!",
                   "E_BADIFIL": "ERROR: Wrong input file!",
                   "E_NOSTYLE": "ERROR: This raster is not properly styled!",
                   "E_NOPSEUDOCOL": "ERROR: Render type is not 'Singleband pseudocolour'",
                  }

    def __init__(self):
        self.err = ''
# =========================================================================================


class BCgetSymbology():
    '''Read symbology parameter from raster layer.'''
    #
    dicotype = {0: 'GrayOrUndefined (single band)',
                1: 'Palette (single band)',
                2: 'Multiband'}
    colmod = {0: 'Discrete', 1: 'Interpolated (Linear)', 2: 'Exact', 3: 'Paletted'}
    clamod = {0: 'N/A - paletted', 1: 'Continuous', 2: 'Equal interval', 3: 'Quantile'}
    iwarning = 0

    def __init__(self, rlayer, verbose=False):
        '''Init class.
           rlayer: QGIS raster layer
           verbose: output details of variables
        '''
        #
        self.rlayer = rlayer
        self.L_Verbose = ''
        self.verbose = verbose
        self.nMode = -1
        self.cm = -1
        self.nC = -1
        self.arL = None
        self.arColo = None
        self.errO = errorObject()
        self.deci = 6
        #
        self.needQML = False
        #
        if rlayer.rasterType() > 1 or rlayer.bandCount() > 1:
            self.errO.err = self.errO.the_strings["E_NOONEBAND"]
        if rlayer.renderer().type() != 'singlebandpseudocolor':
            self.errO.err = self.errO.the_strings["E_NOPSEUDOCOL"]
    # --------------------------------------

    def _format_label(self, t):
        '''Format number with required number of decimals (self.deci).'''
        #
        fmt = '%.' + str(self.deci) + 'f'
        try:
            t = fmt % tofloat(t)
        except:
            self.iwarning += 1
        return t
    # --------------------------------------

    def getCBar(self):
        '''Generate class variables.'''
        #
        if self.errO.err != '':
            return False

        self._rmin = self._format_label(self.rlayer.renderer().classificationMin())
        self._rmax = self._format_label(self.rlayer.renderer().classificationMax())
        #
        self.cm = self.rlayer.renderer().shader().rasterShaderFunction().classificationMode()
        nM = self.rlayer.renderer().shader().rasterShaderFunction().colorRampType()
        if nM == 0:
            nM = 1
        elif nM == 1:
            nM = 0
        self.nMode = nM
        #
        vcpair = self.rlayer.renderer().legendSymbologyItems()
        self.nC = len(vcpair)
        self.arColo = np.zeros((self.nC, 4), np.float32)
        self.arL = np.array(['' * 16] * self.nC, dtype="<U16")
        L0 = ''
        for i, e in enumerate(vcpair):
            if self.verbose and (i < 20 or (self.nC - i) < 20):
                L0 += 'Colour item %d: Value: %s RGBA(%s)\n' % (i, str(e[0]),
                         str(e[1].red())+'-'+str(e[1].green())+'-'+
                         str(e[1].blue())+'-'+str(e[1].alpha()))
            self.arColo[i, 0] = e[1].red() / 255.
            self.arColo[i, 1] = e[1].green() / 255.
            self.arColo[i, 2] = e[1].blue() / 255.
            self.arColo[i, 3] = e[1].alpha() / 255.
            #
            v = e[0].replace('<= ', '').replace('< ', '').replace('> ', '').replace('>= ', '')
            if ' - ' in v:
                v = v.split(' - ')[0]
            self.arL[i] = self._format_label(v)
        if self.arL[0] == self.arL[1]:
            if not np.isnan(tofloat(self._rmin)) and (float(self._rmin) < float(self.arL[0])):
                self.arL[0] = float(self._rmin)
            else:
                self.arL[0] = self._format_label(float(self.arL[0]) - (float(self.arL[2]) - float(self.arL[1])) / 2.)
        if self.arL[-1] == self.arL[-2]:
            if not np.isnan(tofloat(self._rmax)) and (float(self._rmax) > float(self.arL[-1])):
                self.arL[-1] = float(self._rmax)
            else:
                self.arL[-1] = self._format_label(float(self.arL[-1]) + (float(self.arL[-2]) - float(self.arL[-3])) / 2.)
        #
        if self.verbose:
            L = 'Raster type: %s\n' % self.dicotype[self.rlayer.rasterType()]
            L += 'Classification mode: %s\n' % self.clamod[self.cm]
            L += 'Colour ramp type: %s\n' % self.colmod[nM]
            L += 'Classification min: %s, max:%s\n' % (self._rmin, self._rmax)
            L += 'Number of colours/values: %d\n' % len(self.arL)
            self.L_Verbose += L + L0
        #
        return True
    # --------------------------------------

    def __str__():
        return 'This is class BCgetSymbology'
# ===========================================================================================================


class readQML():
    ''' Extract colour scalebar info from a QGIS V3.x QML file.

        Usage:  cr = readQML(qml_file, verbose=True)
                if cr.getCBar():
                    # get colour ramp parameters
                    cr.nMode   - colour ramp type: 0-Discrete, 1-Interpolated, 2-Exact, 3-Paletted
                    cr.cm      - classification mode: 0:N/A , 1-Continuous, 2-Equal interval, 3-Quantile
                    cr.nC      - number of colours
                    cr.arL     - tick labels [label_min, label_max]
                    cr.arColo  - colour ramp (array of [R,G,B,A])
                    #
                    print(cr.L_Verbose) if verbose is True
                else:
                    # Error info
                    error: cr.errO.err

        qml_file: QGIS V3.x .qml filename
        verbose: if Tue set `L_Verbose` with info about the qml read. Default False
    '''

    colmod = {0: 'Discrete', 1: 'Interpolated (Linear)', 2: 'Exact', 3: 'Paletted'}
    clamod = {0: 'N/A', 1: 'Continuous', 2: 'Equal interval', 3: 'Quantile'}
    iwarning = 0

    def __init__(self, the_file, verbose=False):
        '''Variables.'''
        #
        self.errO = errorObject()
        self.the_file = the_file
        self.deci = 6
        self.verbose = verbose
        self.L_Verbose = ''
        #
        self._dom = None
        self._tag = None
        self._origin = ''
        self._items = -1
        self._rtype = -1
        self._rmin = 'min'
        self._rmax = 'max'
        #
        self.nMode = 3  # paletted
        self.cm = 0
        self.nC = -1
        self.arColo = []
        self.arL = []
        #
        self.needQML = True
    # --------------------------------------

    def getCBar(self):
        '''Read and process QML.'''
        #
        # Read QML
        if not self.__read_qml():
            return False
        if self.verbose:
            self.L_Verbose += '----- read_qml\n'
        #
        # Get colouring scheme
        if not self.__getColSch():
            return False
        if self.verbose:
            self.L_Verbose += '----- getColSch\n'
        #
        # Read colour values
        if not self.__getColVals():
            return False
        if self.verbose:
            self.L_Verbose += '----- getColVals\n'
            self.L_Verbose += '=' * 90 + '\n'
        #
        return True   # All OK
    # --------------------------------------

    def _format_label(self, t):
        '''Format number with required number of decimals (self.deci).'''
        #
        fmt = '%.' + str(self.deci) + 'f'
        try:
            t = fmt % float(t) if isfloat(t) else fmt % float(t.replace(',', '.'))
        except:
            self.iwarning += 1
        return t
    # --------------------------------------

    def __read_qml(self):
        '''Read file, parse dom and do some checks.'''
        # 
        try:
            self._dom = get_dom(self.the_file)
            self._tag = self._dom.find("qgis")
        except:
            self.errO.err = self.errO.the_strings["E_BADFIL"]
            return False
        #
        if 'version' in self._tag.attrs:
            v = int(self._tag['version'].strip()[0])
            if self.verbose:
                self.L_Verbose += 'QML version is V%s\n' % self._tag['version']
            if v != 3:   # Version 3
                self.errO.err = self.errO.the_strings["E_BADQML"] % v
                return False
        else:
            self.errO.err = self.errO.the_strings["E_BADFIL"]
            return False
        #
        self._tag = self._dom.find("rasterrenderer")
        if self.verbose:
            self.L_Verbose += 'Raster renderer: %s\n' % str(self._tag.attrs)
        self._rtype = self._tag['type']
        if 'band' not in self._tag.attrs:
            self.errO.err = self.errO.the_strings["E_NOSTYLE"]
            return False
        #
        if int(self._tag['band']) > 1:
            self.errO.err = self.errO.the_strings["E_NOONEBAND"]
            return False
        #
        ori = self._dom.find('GPOrigin')
        if ori is not None:
            self._origin = ori['value']
            if self.verbose:
                self.L_Verbose += 'GeoProc origin: %s\n' % self._origin
        return True
    # --------------------------------------

    def __getColSch(self):
        '''Get colouring scheme.'''
        #
        try:
            self._rmin = self._tag['classificationmin']
            self._rmax = self._tag['classificationmax']
        except:
            self._rmin = 'min'
            self._rmax = 'max'
        #
        if self._rtype.lower() != 'paletted':
            # Get values bounds
            self._tag = self._dom.find("colorrampshader")
            if self.verbose:
                self.L_Verbose += 'Colour ramp shader: %s\n' % ' - '.join(list(['%s: "%s"' % (k, self._tag[k]) for k in self._tag.attrs]))
            ar = '' if 'colorramptype' not in self._tag.attrs else self._tag['colorramptype'].upper()
            if ar == "DISCRETE":
                self.nMode = 0
            elif ar == "INTERPOLATED":    # = LINEAR
                self.nMode = 1
            elif ar == "EXACT":
                self.nMode = 2
            else:
                self.errO.err = self.errO.the_strings["E_NOONEBAND"]
                return False
            #
            # 1: Continuous, 2: Equal interval, 3: Quantile
            self.cm = int(self._tag['classificationmode'])
        #
        return True
    # --------------------------------------

    def __getitems(self):
        '''Get colours/values.'''
        #
        ntag = 'item' if self._rtype.lower() != 'paletted' else 'paletteentry'
        items = self._tag.find_all(ntag)
        n = len(items)
        if self.verbose:
            self.L_Verbose += 'Number of colour slots: %d\n' % n
        if n < 2:
            self.errO.err = self.errO.the_strings["E_NOCOL"]
            return False, None
        #
        return n, items
    # --------------------------------------

    def __initcb(self, n, items):
        '''Init arrays.'''
        #
        valui = str(items[0]['value'])
        if 'inf' in valui and '<' in items[0]['label']:
            if float(self._rmin) < float(items[1]['value']) - .5:
                valui = float(self._rmin)
            else:
                valui = float(items[1]['value']) - (float(items[2]['value']) - float(items[1]['value'])) / 2.
        valua = str(items[-1]['value'])
        if 'inf' in valua and '>' in items[-1]['label']:
            if float(self._rmax) > float(items[-2]['value']) + .5:
                valua = float(self._rmax)
            else:
                valua = float(items[-2]['value']) + (float(items[-2]['value']) - float(items[-3]['value'])) / 2.
        i0 = 0
        self._rmin = str(valui)
        self._rmax = str(valua)
        if self.verbose:
            self.L_Verbose += 'New number of colour slots: %d\n' % n
        #
        self.arColo = np.zeros((n, 4), np.float32)
        self.arL = np.array(['' * 16] * n, dtype="<U16")
        self.arL[-1] = 'inf'
        return n, i0
    # --------------------------------------

    def __getColVals(self):
        '''Read colour values.'''
        #
        n, items = self.__getitems()
        if type(n) is bool:
            return False

        # Build colour ramp
        n, i0 = self.__initcb(n, items)
        #
        for nC, a in enumerate(items):
            # Get each colour (RGBA) and its value/label (arV/tL)
            if 'color' in a.attrs:
                if self.verbose and (nC < 20 or (len(items) - nC) < 20):
                    self.L_Verbose += 'Colour item %d: %s\n' % (nC, str(a.attrs))
                colo = a['color']
                alph = a['alpha']
                valu = a['value']
                self.arColo[i0+nC, 0] = float(int(colo[1:3], 16)) / 255.  # red     [0, 1]
                self.arColo[i0+nC, 1] = float(int(colo[3:5], 16)) / 255.  # green   [0, 1]
                self.arColo[i0+nC, 2] = float(int(colo[5:], 16)) / 255.   # blue    [0, 1]
                self.arColo[i0+nC, 3] = float(alph) / 255.                # alpha   [0, 1]
                if valu != 'inf':      # infinity...
                    self.arL[i0+nC] = self._format_label(valu)   # label: what is shown
            else:
                # Unhandled error
                self.errO.err = self.erO.the_strings["E_BADIFIL"]
                return False

        if items[0]['value'] == 'inf':
            self.arL[0] = self._format_label(self._rmin)
        if self.arL[-1] == 'inf':
            self.arL[-1] = self._format_label(self._rmax)
        self.nC = len(self.arL)
        if self.verbose:
            self.L_Verbose += 'Number of colour elements: %d\n' % self.nC
            self.L_Verbose += 'Number of values: %d\n' % len(self.arL)
            self.L_Verbose += 'Values: [%s]\n' % ', '.join(self.arL)
        #
        self.errO.err = ''
        return True
    # --------------------------------------

    def __str__():
        return 'readQML'
# =========================================================================================


# colour ramp type: 0-Discrete, 1-Interpolated, 2-Exact, 3-Paletted
# classification mode: 0:N/A , 1-Continuous, 2-Equal interval, 3-Quantile
# If colourbar is badly formed, then check that all values are *unique*

class drawCBar():
    '''Draw and save a colour bar.

        Usage:
            myCB = drawCBar(qml_file, **kwgs)
            status = myCB.createCBar()
            if not status:
                print(myCB.err)
            myCB.close()

        ========================================================================
        Required variable:
           qml_file: [str] full name of the QML file to draw colour bar from.
                     The QML file must be a QGIS V3.x file.

        Optional parameters:
           svg_file: [str] (None) name of the svg file storing the colour bar.
                    If None (default) the qml_file is used to set the svg name.

           Colour bar
             orientation: [str] ('horizontal'* | 'vertical'): colour bar orientation
             spacing: [str] ('uniform'* | 'proportional'): colour boxes lengths
             width: [float] colour bar width (15)
             height: [float] colour bar height (0.75)
             drawedges: [bool] draw box around each colour (False)
             inverted: [bool] reverse the direction of the colour bar (False)

           Title
             title: [str] colour bar label ('')
             titlefontname: [str] font name/family: FONTNAME, 'serif', 'sans-serif'*, 'cursive', 'fantasy', 'monospace'
             titlefontsize: [str|int] title font size (28*) number or one of:
                {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}
             titlefontweight: [str|int] title font weight: number [0, 1000] or one of:
                {'ultralight', 'light', 'normal', 'demibold', 'bold'*, 'extra bold'}
             titlecolo: [str] title font colour ('k'* or named colour or '#xxxxxx' value)

           Ticks and label
             tickstep: [int] show label every `ticksteps` ticks (4)
                   can be:
                       -1: to set tickstep to 1 or 4 depending on colourbar length
                       -3: to set 3 (min, half, max) ticks
                       -5: to set 3 (min, half, max) or 5 ticks (min, 1/4, 1/2, 3/4, max)
                            depending on number of colours (default)
             decimal: [int] decimal places for tick labels (3)
             tickfontsize: [str|int] tick label font size (16) or one of the above
             tickcolo: [str] title font colour ('#666666'* or named colour or '#xxxxxx' value)
             ticklength: [float] tick length (8)
           Ticks and labels position
             top: [bool] show thicks/label on top of horizontal colour bar (False)
             bottom: [bool] show thicks/label at bottom of horizontal colour bar (True)
             left: [bool] show thicks/label on left of vertical colour bar (True)
             right: [bool] show thicks/label on right of vertical colour bar (False)
           Tweaking
             tweak_end_replace: [bool] replace last tick with end value (True)
             tweak_end_add: [bool] add end value to ticks array (False)

        Debug parameter (optional):
           verbose: [bool] (False) print information about the QML and ticks
    '''

    the_ERR_str = {'cho_err': "Unknown colour mode / classification mode combination!",
                   'qml_err': "No valid QML file provided!",
                   'rlayer_err': "With raster layer a SVG file name is compulsory!"}

    def __init__(self, qml_file, svg_file=None, noQML=False, **kw):
        '''Initialise with user parameters.'''
        #
        self.the_qml = qml_file
        self.err = ''
        self.L_Verbose = ''
        self.verbose = False if 'verbose' not in kw else bool(kw['verbose'])
        #
        if not noQML:
            # From a QML file
            self.qml = readQML(qml_file, verbose=self.verbose)
            try:
                if not os.path.exists(qml_file):
                    self.err = self.the_ERR_str['qml_err']
                    return
            except:
                self.err = self.the_ERR_str['qml_err']
                return
            self.the_svg = os.path.splitext(qml_file)[0]+'.svg' if svg_file is None else svg_file
        else:
            # Directly from QGIS raster layer (qml_file is rlayer)
            self.qml = BCgetSymbology(qml_file, verbose=self.verbose)
            # We need a svg file name!!!!
            if svg_file is None:
                self.err = self.the_ERR_str['rlayer_err']
                return
            self.the_svg = svg_file
        # -------------------------------------------------
        #
        # Colour bar visual parameters
        #
        # Colour bar orientation and size
        self.ori = 'h' if 'orientation' not in kw else str(kw['orientation'])[0].lower()
        self.ori = 'horizontal' if self.ori != 'v' else 'vertical'
        # Colour boxes lengths
        self.spacing = 'u' if 'spacing' not in kw else str(kw['spacing'])[0].lower()
        self.spacing = 'uniform' if self.spacing != 'p' else 'proportional'
        # Colour bar dimensions
        self.width = 15. if 'width' not in kw else float(kw['width'])
        self.height = 0.75 if 'height' not in kw else float(kw['height'])
        # Draw box around each colour
        self.drawedges = False if 'drawedges' not in kw else bool(kw['drawedges'])
        # Invert colour bar
        self.inverted = False if 'inverted' not in kw else bool(kw['inverted'])

        #Title
        self.label = '' if 'title' not in kw else str(kw['title'])
        self.family = 'sans-serif' if 'titlefontname' not in kw else str(kw['titlefontname'])
        self.titlefontsize = 28. if 'titlefontsize' not in kw else float(kw['titlefontsize'])
        self.titlefontweight = 'bold' if 'titlefontweight' not in kw else str(kw['titlefontweight'])
        self.titlecolo = 'k' if 'titlecolo' not in kw else str(kw['titlecolo'])

        # Ticks to label
        nstep = -5 if 'tickstep' not in kw else int(kw['tickstep'])
        if nstep < 0 and nstep not in [-1, -3, -5]:
            nstep = -5
        self.nstep = 1 if nstep == 0 else nstep
        # Decimal places for tick labels
        self.deci = 2 if 'decimal' not in kw else int(kw['decimal'])
        # Font
        self.tickfontsize = 14. if 'tickfontsize' not in kw else float(kw['tickfontsize'])
        self.tickcolo = '#666666' if 'tickcolo' not in kw else str(kw['tickcolo'])
        self.tz = 8. if 'ticklength' not in kw else float(kw['ticklength'])

        # Ticks position
        self.btop = False if 'top' not in kw else bool(kw['top'])
        self.bbottom = True if 'bottom' not in kw else bool(kw['bottom'])
        self.bleft = True if 'left' not in kw else bool(kw['left'])
        self.bright = False if 'right' not in kw else bool(kw['right'])
        #
        # Tweaking
        self.tweak_end_replace = True if 'tweak_end_replace' not in kw else bool(kw['tweak_end_replace'])
        self.tweak_end_add = False if 'tweak_end_add' not in kw else bool(kw['tweak_end_add'])
        #
        # Who is calling
        self.sourcepg = 'geoprocalgos' if 'source_pg' not in kw else 'CBar4'
    # ----------------------------------------------------------------------------------------

    def close(self):
        '''Close plot.'''
        #
        try:
            _ = plt.close()
        except:
            pass
    # ----------------------------------------------------------------------------------------

    def createCBar(self):
        '''Create the colour bar and save it to svg.

            Return True on success False on problem:
               Check self.err for error description.
        '''
        #
        if self.err != '':
            return False
        #
        b = False
        if not self.qml.getCBar():
            self.err = self.qml.errO.err
            return False
        #
        if self.verbose:
            self.L_Verbose = self.qml.L_Verbose
        #
        if self.__doCB():
            status = self.__save2SVG()
            if status == 'OK':
                b = True
            else:
                self.err = status
        else:
            self.err = 'Error while creating colorbar (doCB).'
            if not self.verbose:
                self.err += '\nPlease re-run with Verbose flag on and\nopen a ticket with the log info on:\nhttps://github.com/BC-Consulting/%s/issues.' % self.sourcepg
        #
        return b
    # ----------------------------------------------------------------------------------------

    def __normalisation(self, bounds, N):
        '''No normalisation.'''
        #
        # colour ramp type: 0-Discrete, 1-Linear (interpolated), 2-Exact, 3-Paletted
        # classification mode: 0:N/A , 1-Continuous, 2-Equal interval, 3-Quantile
        cho = self.qml.cm * 10 + self.qml.nMode
        if cho in [11, 21, 31]:
            self.drawedges = False  # always False
        elif cho in [3, 10, 12, 20, 22, 30, 32]:
            self.spacing = 'uniform'
        else:
            self.err = self.the_ERR_str['cho_err']
            return None
        #
        return mpl.colors.NoNorm()
    # ----------------------------------------------------------------------------------------

    def __colourramp(self):
        '''Define colour ramp.'''
        #
        nn = self.qml.nC
        if self.qml.nMode == 1:
            ncolo = 256 if nn < 256 else nn
        else:
            ncolo = nn
        #
        return mpl.colors.LinearSegmentedColormap.from_list("rmpD", self.qml.arColo, N=ncolo)
    # ----------------------------------------------------------------------------------------

    def __getticks(self):
        '''Set ticks position and labels value.'''
        #
        nn = self.qml.nC
        bounds = list(map(float, self.qml.arL))
        #
        if self.nstep == -5:
            if nn > 7:
                nt = [0, int(nn/4), int(nn/2), nn-int(nn/4), nn-1]
            else:
                nt = [0, int(nn/2), nn-1]
        elif self.nstep == -3:
            nt = [0, int(nn/2), nn-1]
        else:
            if self.nstep == -1:
                if nn <= 5 and max(self.width, self.height) > 10:
                    self.nstep = 1
                else:
                    self.nstep = 4
            #
            nt = [x for x in range(0, len(bounds), self.nstep)]
            #
            if nt[-1] != nn-1:
                if self.tweak_end_replace:
                    nt[-1] = nn-1
                elif self.tweak_end_add:
                    nt.append(nn-1)
        #
        if self.verbose:
            self.L_Verbose += 'CBar indices: [%s]\n' % ', '.join(map(str, nt))
            self.L_Verbose += '      len: Bo %d, Ti %d\n' % (len(bounds), len(nt))
        #
        return bounds, nt
    # ----------------------------------------------------------------------------------------

    def __doCB(self):
        '''Generate colour bar.'''
        #
        if self.ori[0] == 'v' and self.width > self.height:
            self.width, self.height = self.height-.25, self.width
        #
        fig, ax = plt.subplots(figsize=(self.width, self.height))   # , constrained_layout=True)
        if self.height >= 0.75 and self.ori[0] == 'h':
            fig.subplots_adjust(bottom=0.5)
        #
        # colour ramp
        cmap = self.__colourramp()
        if self.verbose:
            n = min(cmap.N, 40)
            spcs = '-' * 90
            self.L_Verbose += 'colour array:\n%s\n%s\n' % (
                '\n'.join(['['+', '.join(map(str, e))+']' for e in self.qml.arColo]), spcs)
            self.L_Verbose += 'colour ramp (first %d colours):\n' % n
            self.L_Verbose += '\n'.join(['['+', '.join(map(str, cmap(e/cmap.N)))+']' for e in range(n)])
            self.L_Verbose += '\n%s\n' % spcs
        #
        # ticks/labels
        bounds, idx = self.__getticks()
        #
        # normalisation
        norm = self.__normalisation(bounds, cmap.N)
        if norm is None:
            return False

        scb = fig.colorbar(
                mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
                cax=ax,
                spacing=self.spacing,
                orientation=self.ori,
                drawedges=self.drawedges,
                fraction=1)
        #
        # Set Title
        scb.set_label(self.label, fontfamily=self.family, fontsize=self.titlefontsize, fontweight=self.titlefontweight, color=self.titlecolo, linespacing=1.4)
        #
        # Set ticks and labels
        fmt = '%0.' + str(self.deci) + 'f'
        labels = [fmt % bounds[i] for i in idx]
        if self.qml.nMode == 0:
            ticksloc = [i-.5 for i in idx]
            ticksloc[0] = idx[0]+.5
            labels[0] = '<= ' + fmt % bounds[1]
            if self.tweak_end_replace or self.tweak_end_add or idx[-1] == self.qml.nC-1:
                labels[-1] = '> ' + labels[-1]
        elif self.qml.nMode == 1:
            n1 = len(bounds) - 1
            ticksloc = [cmap.N - 0.5 - (cmap.N * (n1 - i) / n1) for i in idx]
        else:
            ticksloc = [i for i in idx]
        #
        if self.verbose:
            self.L_Verbose += 'cmap N: %d\n' % cmap.N
            self.L_Verbose += 'norm: %f, %f\n' % (norm.vmin, norm.vmax)
            if cmap.N < 35:
                self.L_Verbose += 'norm: [%s]\n' % ', '.join(map(str, norm.process_value(bounds)))
            self.L_Verbose += 'Ticks location: %s\nTicks label: %s\n' % (', '.join(map(str, ticksloc)), ', '.join(labels))
            self.L_Verbose += '      len: Bo %d, Ti %d, pos %d, lab %d\n' % (len(bounds), len(idx), len(ticksloc), len(labels))
        #
        try:
            scb.set_ticks(ticksloc, labels=labels, fontfamily=self.family, fontsize=self.tickfontsize)
        except Exception as e:
            if self.verbose:
                self.L_Verbose += '\nERROR [cbar/_init_/py:950]: %s\n' % e
            return False
        #
        if self.ori[0] == 'h':
            scb.ax.axes.tick_params(bottom=self.bbottom, top=self.btop, labelbottom=self.bbottom, labeltop=self.btop, length=self.tz, colors=self.tickcolo)
            if self.inverted:
                scb.ax.invert_xaxis()
        else:
            scb.ax.axes.tick_params(right=self.bright, left=self.bleft, labelright=self.bright, labelleft=self.bleft, length=self.tz, colors=self.tickcolo)
            if self.inverted:
                scb.ax.invert_yaxis()
        #
        self.cb = scb
        self.fig = fig
        #
        return True
    # ----------------------------------------------------------------------------------------

    def __save2SVG(self):
        '''Save matplotlib figure (self.fig) to svg file (self.the_svg).'''
        #
        self.fig.savefig(self.the_svg, transparent=True, dpi=300)   # , pad_inches='tight')
        # shutil.copyfile(self.the_svg, os.path.splitext(self.the_svg)[0]+'_ori.svg')
        if self.sourcepg == 'CBar4':
            try:
                self.fig.savefig(os.path.splitext(self.the_svg)[0]+'.png', transparent=True, dpi=300, pad_inches='tight')
            except:
                pass
        #
        titre = os.path.splitext(os.path.split(self.the_svg)[1])[0]
        titre += ' - Ramp type: %s, Classification mode: %s, Number colours: %d' % (
                  self.qml.colmod[self.qml.nMode], self.qml.clamod[self.qml.cm], self.qml.nC)
        # ??
        ar = self.label.split('\n')
        L = 0
        for e in ar:
            L = max(len(e), L)
        # Resize svg file to colourbar content
        my_svg = bc_svg(self.the_svg, titre)
        if my_svg.is_init():
            if not my_svg.auto_process():
                return my_svg.get_error()
            else:
                return 'OK'
        else:
            return my_svg.get_error()

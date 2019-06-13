# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bcCBar3
                            Create a colour scalebar
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

 Custom colour scalebar using maptplotlib
"""
#   Test for dependencies -------------------------------------
try:
    import matplotlib as mpl
    mpl.use('Agg')
    import numpy as np
    from matplotlib.font_manager import FontProperties
    import matplotlib.pyplot as plt
    is_mpl_available = True
except ImportError:
    is_mpl_available = False
try:
    from bs4 import BeautifulSoup
    is_bs4_available = True
except ImportError:
    is_bs4_available = False
#--------------------------------------------------------------

plt.ioff()

import os, re
from xml.dom import minidom
try:
    from PIL import Image
    is_PIL_available = True
except:
    is_PIL_available = False

try:
    from .svg_manip import bc_svg
except:
    from svg_manip import bc_svg
#=========================================================================================

class bcCBarError( RuntimeError ):
    ''' Custom error generator for unsatisfied dependencies. '''
    #
    def message(self):
        return self.args[0] if len(self.args) > 0 else "Exception"
#=========================================================================================

def isfloat(value):
    ''' Test if value can be a float. '''
    #
    try:
        float(value)
        return True
    except ValueError:
        return False
#=========================================================================================

class bcColorBar():
    ''' Draw a colour scalebar from a QGIS V3.x .qml file using paramters passed by user 
        and save it to svg, and optionally to png.

      Usage:
        1) initialise the class with all parameters:
           my_cb = bcColorBar(the_file, the_cbfile, **kwargs)
              the_file: qml file to read (input)
              the_cbfile: colour scalebar svg file (output)
              kwargs: parameters, see __init__ docstring for possible values

        2) check that the object is correctly initialised (e.g. the qml is read)
           if my_cb.get_init_state():
        3)    if ok, draw the colour scalebar
              res = my_cb.draw_cb()
        4)       if ok, save the colour scalebar
                 if res:
                    my_cb.save_cb(Titre)
                 else:
                    print( my_cb.get_error() )
           else:
               print( my_cb.get_error() )

        5) finally close the colour scalebar to clean up the matplotlib drawing space
           my_cb.close()

     -------------------------------------------------------------------------------------
     Accepted .qml's are for one-band-rasters only saved with QGIS V3.x.
     Colour interpolation can be: LINEAR, EXACT, DISCRETE or PALETTED.
     Colour mode can be: Continuous, Equal Interval or Quantile.
     -------------------------------------------------------------------------------------
    '''
    #
    # Info strings: must be public
    the_strings = {"E_BADFIL":"ERROR: Wrong input file (expected a QGIS V3.x .QML file)!",
                   "E_BADQML":"ERROR: Wrong QML version %d. Expected 3!",
                   "E_NOONEBAND":"ERROR: Not a one-band raster!",
                   "E_NOCOL":"ERROR: Not enough colours. Minimum 2!",
                   "E_BADIFIL":"ERROR: Wrong input file!",
                   "E_NOOUTF":"ERROR: No output file specified!",
                   "E_NOINF":"ERROR: No input file specified!",
                   "E_SAVES":"ERROR: Cannot save to svg file after processing!",
                   "E_SAVEP":"ERROR: Cannot save to png file!",
                   "E_NOSTYLE":"ERROR: This raster is not properly styled!",
                   "W_DIRERR":"WARNING: Cannot create /png directory. Save to /temp!",
                   "XTRA_PARAMS":"Additional parameters:",
                   "EM":"and"}
    # Additional parameters. Must be public for internationalisation
    xtra = {'title_align':'Title alignment', 'units_align':'Sub-title alignment',
             'mathfont_set':'Mathfont set', 
             'ticks_font_properties':'Ticks label font properties',
             'title_font_properties':'Title font properties', 
             'units_font_properties':'Sub-title font properties'}

    #-----------------------------------------------------------------
    # Where to put the ticks/labels
    Oo = {  'vertical': ['none', 'left', 'right'],
          'horizontal': ['none', 'top', 'bottom']}
    # Text alignment
    align = ['center', 'right', 'left']
    # Font properties
    fstyle   = ['normal', 'italic', 'oblique']
    fvariant = ['normal', 'small-caps']
    fstretch = ['ultra-condensed', 'extra-condensed', 'condensed', 'semi-condensed', 
                'normal', 'semi-expanded', 'expanded', 'extra-expanded', 'ultra-expanded']
    fweight  = ['ultralight', 'light', 'normal', 'regular', 'book', 'medium', 'roman', 
                'semibold', 'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black']
    fsize    = ['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large']
    # Math font set
    mathfontsets = ['dejavusans', 'dejavuserif', 'cm', 'stix', 'stixsans']
    #-------------------------------------------------------------------------------------

    def __init__(self, the_file, the_cbfile, **kwargs):
        ''' Initialise class with parameters:

        my_cb = bcColorBar(the_file, the_cbfile, **kwargs)

           the_file: QGIS V3.x .qml file to read (input)
         the_cbfile: colour scalebar svg file (output) or empty string
                     If empty string set it with my_cb.set_out_file() before calling
                     my_cb.save_cb()

            kwargs:
                        ori: colour scalebar orientation "vertical"* or "horizontal"
                       deci: number of decimals to display in labels (default: 2)
                      title: title of the colour scalebar. Use ÿ as multilines marker
                      units: sub-title of the colour scalebar (single line)
                       cbwh: ratio width of the scalebar relative to full height (0.1)
                    ticksep: tick separation: every 'ticksep' is shown (default: 1 [>= 1])
                     offset: offset to arrive at nice numbers (default: 0. [-100., 100.])
                  label_alt: True to alternate ticks on both axis. False*
                 label_both: True to label both sides of the colour scalebar. False*
                   label_on: one of 'none', 'both', 'top', 'bottom'*, 'right'*, 'left'
                  font_size: labels font size relative to plot area. Default 4, [.2, 10.]
                      tfont: title font size relative to labels font size (+2)* [-10.,10.]
                      ufont: sub-title font size relative to labels font size (+1)*
                  border_lw: border line width (default 1. [0.0, 5.0])
                 divider_lw: dividers line width, between colours (default 0.0 [0., 2.5])
                title_color: colour of the title ('black'*)
                units_color: colour of the sub-title ('black'*)
               border_color: colour of the border ('black'*)
              divider_color: colour of the dividers ('black'*)
                  breversed: True to reverse display of the colour scalebar. False*
                   with_png: True to also output a png image. False*

            *: default
     -------------------------------------------------------------------------------------
     Accepted .qml's are for one-band-rasters only saved with QGIS V3.x.
     Colour interpolation can be: LINEAR, EXACT, DISCRETE or PALETTED.
     Colour mode can be: Continuous, Equal Interval or Quantile.
     -------------------------------------------------------------------------------------
        '''
        #
        # Do we have a file to act on?
        if the_file.strip() == '':
            self.error  = self.the_strings["E_NOINF"]
            self.isinit = False

        else:
            # Read parameters
            # Class variables
            self.the_file   = the_file
            self.the_cbfile = the_cbfile
            #
            L = 2 if 'deci' not in kwargs else kwargs['deci']
            self.deci = int(self._get_float(L, 2, 0, 12))
            self.ori  = 'vertical' if 'ori' not in kwargs else str(kwargs['ori']).lower()
            if self.ori != 'horizontal':
                self.ori = 'vertical'
            self.Titre = '' if 'title' not in kwargs else kwargs['title']
            L = 'black' if 'title_color' not in kwargs else kwargs['title_color']
            self.title_color = L
            self.Units = '' if 'units' not in kwargs else kwargs['units']
            L = 'black' if 'units_color' not in kwargs else kwargs['units_color']
            self.units_color = L
            L = 0.1 if 'cbwh' not in kwargs else kwargs['cbwh']
            self.cbwh = self._get_float(L, .1, .001, 1.)
            L = False if 'label_alt' not in kwargs else bool(kwargs['label_alt'])
            self.LabelsAlt = L
            if L:
                self.LabelsonBoth = False
            else:
                L = False if 'label_both' not in kwargs else bool(kwargs['label_both'])
                self.LabelsonBoth = L
            de = self.Oo[self.ori][-1] # default tick position
            L = de if 'label_on' not in kwargs else str(kwargs['label_on']).lower()
            self.Labelson = de if L not in self.Oo[self.ori] else L
            L = 4 if 'font_size' not in kwargs else kwargs['font_size']
            self.fntSize = self._get_float(L, 4., .2, 10.)
            L = 1.0 if 'border_lw' not in kwargs else kwargs['border_lw']
            self.border_lw = self._get_float(L, 1.0, 0., 5.)
            L = 2 if 'tfont' not in kwargs else kwargs['tfont']
            self.tfont = self.fntSize + self._get_float(L, 2., -10., 10.)
            L = 1 if 'ufont' not in kwargs else kwargs['ufont']
            self.ufont = self.fntSize + self._get_float(L, 1., -10., 10.)
            L = 'black' if 'border_color' not in kwargs else kwargs['border_color']
            self.border_color = L
            L = 0.0 if 'divider_lw' not in kwargs else kwargs['divider_lw']
            self.divider_lw = self._get_float(L, 0., 0., 2.5)
            L = 'black' if 'divider_color' not in kwargs else kwargs['divider_color']
            self.divider_color = L
            self.b_png = False if 'with_png' not in kwargs else bool(kwargs['with_png'])
            #
            # Local variables
            breversed = False if 'breversed' not in kwargs else bool(kwargs['breversed'])
            L = 1 if 'ticksep' not in kwargs else kwargs['ticksep']
            ticksep = int(self._get_float(L, 1, 1, 1000000))
            L = 0 if 'offset' not in kwargs else kwargs['offset']
            offset = self._get_float(L, 0., -100., 100.)
            #
            # Other class variables
            self.set_display = False     # True to show the colour scalebar
            self.dpi         = 300
            self.nMode       = 0
            self.cm          = 0
            #
            self.arV         = None
            self.arL         = None
            self.ticksV      = None
            self.ticksL      = None
            self.vramp       = None
            self.cramp       = None
            self.fig         = None
            self.ticksep     = ticksep
            self.offset      = offset
            self.breversed   = breversed
            self.isxtra      = False
            #
            # Read and parse qml file
            #  results are array of values, labels & colours, and type of colour scalebar
            self.isinit = self._read_qml()
            #
            if self.isinit:
                if breversed:
                    # Reverse the colour map
                    self.cramp = np.flip(self.cramp, axis=0)
                    self.arV   = self.arV[::-1]
                    self.arL   = self.arL[::-1]
                    self.vramp = self.vramp[::-1]
                    self.cramp = self.cramp[::-1]

                if ticksep > 1:
                    if self.nMode !=1:
                        offset = 0.
                    #  draw tick every    n   values
                    msk = [True if ((offset + s) % ticksep) == 0 else False 
                                                            for s in range(len(self.arL))]
                    if (msk[-1] == False and 
                        self.arV[-1] - self.arV[-2] > self.arV[-2] - self.arV[-3]):
                        msk[-1] = True
                    #  set ticks to display
                    self.ticksV = self.arV[msk]
                    self.ticksL = self.arL[msk]
                else:
                    self.ticksV = self.arV
                    self.ticksL = self.arL
                if self.LabelsAlt:
                    V = self.ticksV
                    mskalt1 = [True if (i % 2) == 0 else False for i in range(len(V))]
                    mskalt2 = [True if (i % 2) == 1 else False for i in range(len(V))]
                    self.ticksLa = self.ticksL[mskalt2]
                    self.ticksVa = self.ticksV[mskalt2]
                    self.ticksL  = self.ticksL[mskalt1]
                    self.ticksV  = self.ticksV[mskalt1]
                else:
                    self.ticksLa = []
                    self.ticksVa = []

            self.arV = None
            self.arL = None
            #
            # Additional parameters: default values
            self.title_align = 'center'
            self.units_align = 'center'
            self.ticks_font_properties = FontProperties()
            self.title_font_properties = FontProperties()
            self.units_font_properties = FontProperties()
            self.mathfont_set = 'dejavusans'

            self.title_font_properties.set_family('sans-serif')
            self.title_font_properties.set_size(self.tfont)
            self.title_font_properties.set_weight('bold')

            self.units_font_properties.set_family('sans-serif')
            self.units_font_properties.set_size(self.ufont)
            self.units_font_properties.set_weight('medium')

            self.ticks_font_properties.set_family('sans-serif')
            self.ticks_font_properties.set_size(self.fntSize)
    #-------------------------------------------------------------------------------------

    def _check_font_properties(self, font0, weight='normal'):
        ''' Check if the given font properties are valid. '''
        #
        font = self._get_dict(font0)
        #
        fontp = FontProperties()
        #      6 parameters in a font properties dictionary
        vkey = ['family', 'style', 'variant', 'stretch', 'weight', 'size']
        for k in font:
            if k not in vkey:
                return fontp
            #
            if k == 'style':
                if not font[k] in self.fstyle:
                    font[k] = 'normal'
            else:
                font['style'] = 'normal'
            if k == 'variant':
                if not font[k] in self.fvariant:
                    font[k] = 'normal'
            else:
                font['variant'] = 'normal'
            if k == 'stretch':
                if not isfloat(font[k]):
                    if font[k] not in self.fstretch:
                        font[k] = 'normal'
                else:
                    if not (0. < float(font[k]) < 1000.):
                        font[k] = 'normal'
            else:
                font['stretch'] = 'normal'
            if k == 'weight':
                if not isfloat(font[k]):
                    if font[k] not in self.fweight:
                        font[k] = weight
                else:
                    if not (0. < float(font[k]) < 1000.):
                        font[k] = weight
            else:
                font['weight'] = weight
            if k == 'size':
                if not isfloat(font[k]):
                    if font[k] not in self.fsize:
                        font[k] = 12.
                else:
                    if not (0. < float(font[k]) < 100.):
                        font[k] = 12.
            else:
                font['size'] = 12.
        #
        fontp.set_family(font['family'])
        fontp.set_size(font['size'])
        fontp.set_weight(font['weight'])
        fontp.set_variant(font['variant'])
        fontp.set_stretch(font['stretch'])
        fontp.set_style(font['style'])
        #
        return fontp
    #-------------------------------------------------------------------------------------

    def _fnt_to_str(self, fp):
        ''' Return a string from font properties. '''
        #
        v = 'Family: ' + str(fp.get_family())
        v += ', Size: ' + str(fp.get_size())
        v += ', Weight: ' + str(fp.get_weight())
        v += ', Variant: ' + str(fp.get_variant())
        v += ', Style: ' + str(fp.get_style())
        v += ', Stretch: ' + str(fp.get_stretch())
        return v
    #-------------------------------------------------------------------------------------

    def _get_float(self, L, defaut, boundMin, boundMax):
        ''' Make sure L is a float boundMin < L < boundMax or return default if not. '''
        #
        if not isfloat(L):
            L = defaut
        if not (boundMin <= float(L) <= boundMax):
            L = defaut
        #
        return float(L)
    #-------------------------------------------------------------------------------------

    def _get_bounds(self, bb):
        ''' ReturnL X0, Y0, Xwidth, Yheight. '''
        #
        if type(bb) is mpl.transforms.Bbox:
            w = bb.x1 - bb.x0
            h = bb.y1 - bb.y0
            return [bb.x0, bb.y0, w, h]
        else:
            w = bb[1][0] - bb[0][0]
            h = bb[1][1] - bb[0][1]
            return [bb[0][0], bb[0][1], w, h]
    #-------------------------------------------------------------------------------------

    def _get_colour(self, v):
        ''' Convert to colour. '''
        #
        #v="255,255,212,255"
        return [float(x) / 255. for x in v.split(',')]
    #-------------------------------------------------------------------------------------

    def _get_dict(self, dic):
        ''' Create and return a dictionary for a dict-like string. One-level only.
            Any dict-like string as value of top level key is kept as is.
        '''
        #
        dic = dic.strip()
        print(dic)
        if dic[0] != '{' or dic[-1] != '}':
            return {}
        n1, n2 = dic.count('{'), dic.count('}')
        if n1 != n2:
            return {}
        #
        q = ''.join([str(c) for c in dic])
        q = re.sub(r',\s*', ',', q)
        q = q[1:-1].replace('"', '').replace("'","")
        print(q)
        if n1 == 1:
            q = q.split(',')
            return {kv.split(':')[0]:kv.split(':')[1] for kv in q if kv != ''}
        else:
            n1 -= 1
            ar = {}
            for n in range(n1):
                i1 = q.find('{')
                i2 = q.find('}', i1) + 1
                k = 'BCCC_%05d' % n 
                ar[k] = q[i1:i2]
                q = q[:i1] + k + q[i2:] 
            q = q.split(',')
            a = {kv.split(':')[0]:kv.split(':')[1] for kv in q if kv != ''}
            for ka in a:
                for k in ar:
                    if k in a[ka]:
                        a[ka] = a[ka].replace(k, ar[k])
            return a
    #-------------------------------------------------------------------------------------

    def _format_label(self, t):
        ''' Format number with required number of decimals (self.deci). '''
        #
        fmt = '%.' + str(self.deci) + 'f'
        try:
            t = fmt % float(t)
        except:
            pass
        return t
    #-------------------------------------------------------------------------------------

    def _read_qml(self):
        ''' Extract colour scalebar info from a QGIS V3.x QML file.

        return: True on success, False on error (check get_error() for error message)
        '''
        #
        # number of decimal to use for display of ticks label
        the_file = self.the_file
        #
        # Read file, parse dom and do some checks
        try:
            dom = minidom.parse(the_file)
            tag = dom.getElementsByTagName("qgis")[0]
        except:
            self.error = self.the_strings["E_BADFIL"]
            return False
        #
        if tag.hasAttribute('version'):
            v = int(tag.getAttribute('version').strip()[0])
            if v != 3: #Version 3
                self.error = self.the_strings["E_BADQML"] % v
                return False
        #
        tag = dom.getElementsByTagName("rasterrenderer")[0]
        rtype = tag.getAttribute('type')
        if not tag.hasAttribute('band'):
            self.error = self.the_strings["E_NOSTYLE"]
            return False            
        rband = tag.getAttribute('band')
        if int(rband) > 1:
            self.error = self.the_strings["E_NOONEBAND"]
            return False
        #--------------------------------------

        # Get colouring scheme
        if rtype.lower() == 'paletted':
            ntag  = 'paletteEntry'
            nMode = 3
            cm    = 0
            rmin  = 'min'
            rmax  = 'max'
        else:
            # Get values bounds
            try:
                rmin = tag.getAttribute('classificationMin')
                rmax = tag.getAttribute('classificationMax')
            except:
                rmin = 'min'
                rmax = 'max'
            tag = dom.getElementsByTagName("colorrampshader")[0]
            ar = tag.getAttribute('colorRampType').upper()
            ntag = 'item'
            if ar == "DISCRETE":
                nMode = 0
            elif ar == "INTERPOLATED":    # = LINEAR
                nMode = 1
            elif ar == "EXACT":
                nMode = 2
            else:
                self.error = self.the_strings["E_NOONEBAND"]
                return False
            #
            # 1: Continuous, 2: Equal interval, 3: Quantile
            cm = int(tag.getAttribute('classificationMode'))  

        # Read colour values
        items = tag.getElementsByTagName(ntag)
        n = len(items)
        if n < 2:
            self.error = self.the_strings["E_NOCOL"]
            return False

        if nMode != 1:
            # Discrete: Number of colours is one less than number of ticks
            arColo = np.zeros((n, 4), np.float32)
            arV    = np.zeros(n + 1, np.float32)
            tL     = np.array(['' * 16] * (n + 1), dtype="<U16")
            ioff = 1
        else:
            # Otherwise: Number of colours = number of ticks
            arColo = np.zeros((n, 4), np.float32)
            arV    = np.zeros(n, np.float32)
            tL     = np.array(['' * 16] * n, dtype="<U16")
            ioff = 0

        # Build colour ramp
        for nC, a in enumerate(items):
            #Get each colour (RGBA) and its value/label (arV/tL)
            if a.hasAttribute('color'):
                colo = a.getAttribute('color')
                alph = a.getAttribute('alpha')
                valu = a.getAttribute('value')
                labl = a.getAttribute('label')
                arColo[nC, 0] = float(int(colo[1:3],16)) / 255. # red     [0, 1]
                arColo[nC, 1] = float(int(colo[3:5],16)) / 255. # green   [0, 1]
                arColo[nC, 2] = float(int(colo[5:],16)) / 255.  # blue    [0, 1]
                arColo[nC, 3] = float(alph) / 255.              # alpha   [0, 1]
                if valu == 'inf': # infinity...
                    if rmax != 'max':
                        valu = rmax
                    else:
                        valu = 2 * arV[nC - 1] - arV[nC -2]
                    labl = rmax
                arV[nC + ioff] = float(valu)                  # value: colour upper border
                tL[nC + ioff]  = self._format_label(labl)     # label: what is shown
            else:
                # Unhandled error
                self.error = self.the_strings["E_BADIFIL"]
                return False

        # Lowest colour border
        if nMode == 0:
            # Discrete
            arV[0] = rmin
            tL[0]  = self._format_label(rmin)
        elif nMode != 1:
            # Exact/Paletted
            arV[0] = '%.0f' % (2 * arV[1] - arV[2] - .5)

        # Adjust for bad palettes
        if cm == 3:
            # Quantile: deal with badly designed colour ramp (remove colours)
            msk = []
            for i in range(1, nC):
                if arV[i] == arV[i - 1]:
                    msk.append(i - 1)
            arV = np.delete(arV, msk)
            tL = np.delete(tL, msk)
            arColo = np.delete(arColo, msk, axis=0)
            nC = len(arV) - 1

        if nC == 1 and nMode < 2:
            # only two values: min, min, max
            # correct to: min, half, max
            if arV[0] == arV[1]:
                arV[1] = (arV[0] + arV[2]) / 2.
                tL[1] = self._format_label(arV[1])

        #-------------------------------------------------------------------------
        # Now, define tick locations
        vmin = arV.min()
        vmax = arV.max()
        if nMode < 2:
            # Linear and Discrete: ticks position = colours border
            tV = arV
        else:
            # EXACT or PALETTED
            # values = index. Colour scalebar is based on index
            # labels are what is read from file
            # Here number of colours = number of ticks
            # ticks plot in the middle of the colour box
            # Adjust ticks position, but ticks label stay the same.
            tV = np.array([(arV[i] + arV[i - 1]) / 2. for i in range(1, len(arV))])
            tL = tL[1:]
        #
        # Normalise ticks position to [0, 1]
        tV = (tV - vmin) / (vmax - vmin)

        #-------------------------------------------------------------------------
        # Finally, create the colour ramp to use
        nC += 1
        if nMode == 1:
            # Linear - Nvalues = Ncolors
            # ----------------
            # ||||||||||||||||   many colours
            # ----------------
            # |  |  |  |  |  |   v
            #                                                          dummy, but large...
            rmp  = mpl.colors.LinearSegmentedColormap.from_list("rmpL", arColo, N = 512)
            rgba = rmp(np.linspace(0., 1., 512))
            norm = np.linspace(0., 1., 512)

        elif nMode == 0:        
            # Discrete - Nvalues = Ncolors +1
            #  -- -- -- -- --
            # |  |  |  |  |  |    ncolo & ncolo+1 stops
            #  -- -- -- -- --
            # |  |  |  |  |  |   v=>ncolo+1
            #                                                           number of colors
            rmp  = mpl.colors.LinearSegmentedColormap.from_list("rmpD", arColo, N = nC)
            rgba = rmp(np.linspace(0., 1., nC))
            norm = np.linspace(0., 1., nC+1)

        else:
            # Exact/Palette - Nvalues = Ncolors (but offset)
            #  --- --- --- --- ---
            # |   |   |   |   |   |    ncolo & ncolo+1 stops
            #  --- --- --- --- ---
            #   |   |   |   |   |      v=>ncolo
            #                                                          number of colors
            rmp = mpl.colors.LinearSegmentedColormap.from_list("rmpE", arColo, N = nC)
            rgba = rmp(np.linspace(0., 1., nC))
            norm = np.linspace(0., 1., nC+1)

        # Set colour info
        self.vramp = norm         # Normalised colours edge position to [0, 1]
        self.cramp = rgba
        self.arV   = tV
        self.arL   = tL
        self.nMode = nMode
        self.cm    = cm
        self.error = ''
        #
        return True
    #-------------------------------------------------------------------------------------

    def _set_units(self, L, cax, fontd, colo = 'black', pad = None):
        ''' Use axes title object to plot units/title last line.
                L: text to plot
              cax: axes to use
            fontd: font properties
             colo: colour
              pad: vertical distance from axes

            Return the vertical position of the bottom position of the next line
        '''
        #
        plt.draw()
        inva = cax.transData.inverted()                            # convert to Data space
        #
        un = cax.set_title(L, loc=self.units_align, fontproperties=fontd, color=colo,
                           pad=pad)
        #
        plt.draw()
        ubb = un.get_window_extent(self.fig.canvas.get_renderer()) # in display space
        uca = inva.transform([[ubb.x0, ubb.y0],[ubb.x1, ubb.y1]])  # in data space
        ul, ub, uw, uh = self._get_bounds(uca)
        #
        if L.strip() != '':
            ym = ub + uh * 1.25
        else:
            ym = ub
        return ym
    #-------------------------------------------------------------------------------------

    def _set_label_position(self):
        ''' Define plotting parameters.

            Return positional flags and tweaking parameter
        '''
        #
        # Fixed parameters
        Length = 3.14960632
        Width  = 1.18110237

        # Labels position
        labTa, labBa, labRa, labLa = False, False, False, False
        twk = 0.
        if self.ori == 'horizontal':
            xp = Length
            yp = Width
            if self.LabelsonBoth:
                labT, labB, labR, labL = True, True, False, False
                twk = 10.
            elif self.LabelsAlt:
                labT, labB, labR, labL     = True, False, False, False  # top
                labTa, labBa, labRa, labLa = False, True, False, False  # bottom
                twk = 10.                
            else:
                if self.Labelson == 'top':
                    labT, labB, labR, labL = True, False, False, False
                    twk = 10.
                else:
                    labT, labB, labR, labL = False, True, False, False
                    twk = 3.5
        else:
            twk = 5.0
            yp = Length
            xp = Width
            if self.LabelsonBoth:
                labT, labB, labR, labL = False, False, True, True
            elif self.LabelsAlt:
                labT, labB, labR, labL     = False, False, False, True  # left
                labTa, labBa, labRa, labLa = False, False, True, False  # right
            else:
                if self.Labelson == 'left':
                    labT, labB, labR, labL = False, False, False, True
                else:
                    labT, labB, labR, labL = False, False, True, False
        #
        self.xp, self.yp = xp, yp
        return labT, labB, labR, labL, labTa, labBa, labRa, labLa, twk
    #-------------------------------------------------------------------------------------

    def _save_png(self, imgF):
        ''' Save and crop a png file.

            return: True on success, False on error (call get_error() for info)
        '''
        #
        try:
            # Save as a large png and crop the saved image
            # We *5 the width & height because it doesn't work otherwise...
            box = mpl.transforms.Bbox.from_bounds(-1., -1., self.xp * 5., self.yp * 5.)
            self.fig.savefig(imgF, transparent = True, dpi = 300, bbox_inches = box)

            # Crop png image
            image = Image.open(imgF)
            image.load()
            image_data = np.asarray(image)

            msk  = image_data[:,:,3] > 0
            col  = msk.sum(axis = 0)
            row  = msk.sum(axis = 1)
            ncol = np.where(col > 0)[0]
            nrow = np.where(row > 0)[0]
            img_new = image_data[min(nrow):max(nrow) + 1, min(ncol):max(ncol) + 1, :]

            new_image = Image.fromarray(img_new)
            new_image.save(imgF)
        except:
            self.error = self.the_strings["E_SAVEP"]
            return False

        return True
    #-------------------------------------------------------------------------------------

    def close(self):
        ''' Close matplotlib plot. '''
        #
        plt.close()
    #-------------------------------------------------------------------------------------

    def get_init_state(self):
        ''' Return the initialisation state: true of false.
            Check this property after initialisation of the class
            If false call get_error() to have an error message.
        '''
        #
        return self.isinit
    #-------------------------------------------------------------------------------------

    def get_error(self):
        ''' Return the current error message. '''
        #
        return self.error
    #-------------------------------------------------------------------------------------

    def get_value(self, param):
        ''' Return the value of param. '''
        #
        if param == 'ori':
            return self.ori
        elif param == 'deci':
            return self.deci
        elif param == 'title':
            return self.Titre
        elif param == 'units':
            return self.Units
        elif param == 'cbwh':
            return self.cbwh
        elif param == 'ticksep':
            return self.ticksep
        elif param == 'offset':
            return self.offset
        elif param == 'label_alt':
            return self.LabelsAlt
        elif param == 'label_both':
            return self.LabelsonBoth
        elif param == 'label_on':
            return self.Labelson
        elif param == 'font_size':
            return self.fntSize
        elif param == 'tfont':
            return self.tfont
        elif param == 'ufont':
            return self.ufont
        elif param == 'with_png':
            return self.b_png
        elif param == 'border_lw':
            return self.border_lw
        elif param == 'divider_lw':
            return self.divider_lw
        elif param == 'divider_color':
            return self.divider_color
        elif param == 'border_color':
            return self.border_color
        elif param == 'title_color':
            return self.title_color
        elif param == 'units_color':
            return self.units_color
        elif param == 'breversed':
            return self.breversed
        elif param == 'title_align':
            return self.title_align
        elif param == 'units_align':
            return self.units_align
        elif param == 'mathfont_set':
            return self.mathfont_set
        elif param == 'ticks_font_properties':
            return self._fnt_to_str(self.ticks_font_properties)
        elif param == 'title_font_properties':
            return self._fnt_to_str(self.title_font_properties)
        elif param == 'units_font_properties':
            return self._fnt_to_str(self.units_font_properties)
        else:
            return ''
    #-------------------------------------------------------------------------------------

    def get_params_used(self, in_file, the_params):
        ''' Return the description and value of the parameters used. '''
        #
        strused = '<p>'
        for param in sorted(the_params, key=the_params.__getitem__):
            L = the_params[param][1] + ' = '
            if param == 'THE_LAYER':
                v = in_file
            elif param == 'XTRA_PARAM':
                L = self.the_strings['XTRA_PARAMS']
                v = '<br/>'
                for k, x in self.xtra.items():
                    v += '&nbsp;' * 4 + x + ': ' + str(self.get_value(k)) + '<br/>'
            elif param == 'OUTPUT':
                v = self.the_cbfile
            else:
                # value used by bcCBar and not the one provided in input
                v = str(self.get_value(param.lower()))
            #
            L = L.replace('<', '&lt;').replace('>', '&gt;')
            v = v.replace('<', '&lt;').replace('>', '&gt;')
            v = v.replace('&lt;br/&gt;', '<br/>')
            strused += L + v + '<br/>'
        #
        if self.b_png:
            v = self.the_cbfile[:-3] + 'png'
            strused += ' <em>' + self.the_strings["EM"] + '</em> ' + v + '<br/>'
        return (strused[:-5] + '</p>\n').replace('<br/>','<br/>\n')
    #-------------------------------------------------------------------------------------

    def set_extras(self, dic):
        ''' Set additional parameters to fine-tune the appearance of the colour scalebar.

            dic:
                title_align: title text alignment one of ['center'*, 'right', 'left']
                units_align: sub-title text alignment one of ['center'*, 'right', 'left']
      ticks_font_properties: dictionary of valid font properties for ticks label {}*
      title_font_properties: dictionary of valid font properties for title {}*
      units_font_properties: dictionary of valid font properties for sub-title {}*
               mathfont_set: font-set use for displaying mathtext, one of:
                                  ['dejavusans'*, 'dejavuserif', 'cm', 'stix', 'stixsans']

            * default
        '''
        #
        kwargs = self._get_dict(dic)
        if kwargs == {}:
            return False

        if 'title_align' in kwargs:
            L = kwargs['title_align'].lower()
            self.title_align = 'center' if L not in self.align else L
        if 'units_align' in kwargs:
            L = kwargs['units_align'].lower()
            self.units_align = 'center' if L not in self.align else L
        if 'mathfont_set' in kwargs:
            L = kwargs['mathfont_set'].lower()
            self.mathfont_set = 'dejavusans' if L not in self.mathfontsets else L
        if 'ticks_font_properties' in kwargs:
            L = kwargs['ticks_font_properties']
            self.ticks_font_properties = self._check_font_properties(L)
        if 'title_font_properties' in kwargs:
            L = kwargs['title_font_properties']
            self.title_font_properties = self._check_font_properties(L)
        if 'units_font_properties' in kwargs:
            L = kwargs['units_font_properties']
            self.units_font_properties = self._check_font_properties(L)
        #
        self.isxtra = True
        return True
    #-------------------------------------------------------------------------------------

    def set_out_file(self, fil):
        ''' Sets the output file name (full path) if not set during initialisation. '''
        #
        self.the_cbfile = fil
    #-------------------------------------------------------------------------------------

    def set_dpi(self, dpi):
        ''' Sets the figure dpi (default: 300).
            Must be called before plotting the colour scalebar.
        '''
        #
        self.dpi = dpi
    #-------------------------------------------------------------------------------------

    def draw_cb(self):
        ''' Draw a colour scalebar using the parameters passed by the user.

            return: True on success, False on error (check get_error() for error message)
        '''
        #
        ori       = self.ori
        ticksV    = self.ticksV
        ticksL    = self.ticksL
        ticksVa   = self.ticksVa
        ticksLa   = self.ticksLa
        cramp     = self.cramp
        vramp     = self.vramp
        Titre     = self.Titre.strip()
        Units     = self.Units.strip()
        cbwh      = self.cbwh
        border_lw = self.border_lw
        border_cl = self.border_color
        div_lw    = self.divider_lw
        div_cl    = self.divider_color
        title_cl  = self.title_color
        units_cl  = self.units_color
        #
        labT,labB,labR,labL, labTa,labBa,labRa,labLa, twk = self._set_label_position()
        # Fonts to be used for title and units
        fontu = self.units_font_properties
        fontt = self.title_font_properties

        fig = plt.figure(dpi=self.dpi, figsize=(self.xp, self.yp), #facecolor='c', 
                         clear=True)  #, constrained_layout=False)
        self.fig = fig

        mpl.rcParams['mathtext.fontset'] = self.mathfont_set

        # Define axis
        if ori == 'horizontal':
            cax = fig.add_axes([0., 0., 1., cbwh])
            xmin, xmax = vramp[0], vramp[-1]
            ymin, ymax = 0., 1.
            cax.set_xlim([xmin, xmax])
            cax.set_ylim([ymin, ymax])
            xl, yl, wl, hl = 0., .4, 1., .6
            if self.LabelsAlt:
                axa = cax.twiny()
                axa.set_xlim([xmin, xmax])
        else:
            cax = fig.add_axes([0.5 - cbwh / 2., 0., cbwh, 0.8])
            xmin, xmax = 0., 1.
            ymin, ymax = vramp[0], vramp[-1]
            cax.set_xlim([xmin, xmax])
            cax.set_ylim([ymin, ymax])
            xl, yl, wl, hl = 0., 0.8, 1., 0.2
            if self.LabelsAlt:
                axa = cax.twinx()
                axa.set_ylim([ymin, ymax])

        # Define and set ticks and labels
        if not self.LabelsonBoth and self.Labelson == 'none':
            cax.set_axis_off()
        else:
            if ori == 'horizontal':
                # ticks and labels
                cax.set_xticks(ticksV)
                cax.set_xticklabels(ticksL, fontproperties=self.ticks_font_properties)
                if self.LabelsAlt:
                    axa.set_xticks(ticksVa)
                    axa.set_xticklabels(ticksLa, fontproperties=self.ticks_font_properties)
                else:
                    cax.get_yaxis().set_ticks([])
            else:
                # ticks and labels
                cax.set_yticks(ticksV)
                cax.set_yticklabels(ticksL, fontproperties=self.ticks_font_properties)
                if self.LabelsAlt:
                    axa.set_yticks(ticksVa)
                    axa.set_yticklabels(ticksLa, fontproperties=self.ticks_font_properties)
                else:
                    cax.get_xaxis().set_ticks([])

            # Ticks and labels options  labelsize=fntSize, 
            if self.LabelsAlt:
                cax.tick_params(bottom=labT, top=labT, left=labL, right=labL,
                                labelbottom=labB, labeltop=labT, labelleft=labL,
                                labelright=labR, width=0.4, length=2, direction='out',
                                pad=1, colors=border_cl)
                axa.tick_params(bottom=labBa, top=labBa, left=labRa, right=labRa,
                                labelbottom=labBa, labeltop=labTa, labelleft=labLa,
                                labelright=labRa, width=0.4, length=2, direction='out',
                                pad=1, colors=border_cl)
            else:
                cax.tick_params(bottom=labB, top=labT, left=labL, right=labR,
                                labelbottom=labB, labeltop=labT, labelleft=labL,
                                labelright=labR, width=0.4, length=2, direction='out',
                                pad=1, colors=border_cl)

        # Other dummy axes
        clg = fig.add_axes([xl, yl, wl, hl])
        clg.get_yaxis().set_ticks([])
        clg.get_xaxis().set_ticks([])
        clg.set_axis_off()

        # Draw colour scalebar
        nC = len(vramp) - 1
        if ori == 'horizontal':
            for i in range(nC):
                r = mpl.patches.Rectangle([vramp[i], 0.0], vramp[i+1] - vramp[i], 1.0, 
                                          fill = True, facecolor = cramp[i],
                                          linewidth = div_lw, edgecolor = div_cl)
                cax.add_patch(r)
        else:
            for i in range(nC):
                r = mpl.patches.Rectangle([0.0, vramp[i]], 1.0, vramp[i+1] - vramp[i], 
                                          fill = True, facecolor = cramp[i],
                                          linewidth = div_lw, edgecolor = div_cl)
                cax.add_patch(r)

        # Draw frame
        cax.set_frame_on(False)
        fr = mpl.patches.Rectangle([xmin, ymin], xmax - xmin, ymax - ymin, fill = False,
                                   linewidth = border_lw, edgecolor = border_cl)
        cax.add_patch(fr)

        # Plot Title and sub-title -------------------------------------------------------
        # Draw units
        if Units != '':
            ym = self._set_units(Units, cax, fontu, colo = units_cl, pad = twk)
        else:
            if not self.LabelsonBoth and self.Labelson=='bottom' and ori=='horizontal':
                twk = 0.9
            elif ori=='horizontal':
                twk = 1.3
            else:
                twk = 1.0
            ym = self._set_units(' ', cax, fontu) * twk

        if Titre != '':
            # Draw title
            if self.title_align == 'left':
                xm = xmin
            elif self.title_align == 'right':
                xm = xmax
            else:
                xm = (xmin + xmax) / 2.
            Titre = Titre.replace('ÿ', '\n')        # use native multilines capability!!!
            cax.text(xm, ym, Titre,
                    horizontalalignment = self.title_align,
                    verticalalignment   = 'bottom',
                    fontproperties      = fontt,
                    color               = title_cl,
                    transform           = cax.transData)

        fig.tight_layout()
        if self.set_display:
            # Show colour scalebar
            plt.show()
        #
        #
        return True
    #-------------------------------------------------------------------------------------

    def save_cb(self):
        ''' Save and crop colour scalebar.

            return: True on success, False on error (call get_error() for info)
        '''
        #
        self.error = ''
        if self.the_cbfile.strip() == '':
            self.error = self.the_strings["E_NOOUTF"]
            return False

        fil = os.path.splitext(self.the_cbfile)[0]
        imgFileV = fil + '.svg'

        # Save to svg for further manipulation.
        #  Full image will be partly outside page, but recoverable...
        self.fig.savefig(imgFileV, transparent = True, dpi = 300)

        # Resize svg file to colourbar content
        my_svg = bc_svg(imgFileV)
        if my_svg.is_init():
            if not my_svg.auto_process():
                self.error = self.the_strings["E_SAVES"] + '\n' + my_svg.get_error()
        else:
            self.error = my_svg.get_error()

        if self.b_png:
            # Also save a png file and crop it
            imgFileN = fil + '.png'
            self._save_png(imgFileN)

        return True
#=========================================================================================
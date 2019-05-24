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

import matplotlib as mpl
mpl.use('agg')

import os
from xml.dom import minidom
import numpy as np
from PIL import Image
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
plt.ioff()

try:
    from .svg_manip import bc_svg
except ModuleNotFoundError:
    raise
except:
    from svg_manip import bc_svg
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
    # Error strings
    the_strings = ["ERROR: Wrong input file (expected a QGIS V3.x .QML file)!",
                   "ERROR: Wrong QML version %d. Expected 3!",
                   "ERROR: Not a one-band raster!",
                   "ERROR: Not enough colours. Minimum 2!",
                   "ERROR: Wrong input file!",
                   "ERROR: No output file specified!",
                   "ERROR: No input file specified!",
                   "WARNING: Cannot create /png directory. Save to /temp!",
                   "ERROR: Cannot save to svg file after processing!",
                   "ERROR: Cannot save to png file!",
                   "ERROR: This raster is not properly styled!"]

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
            self.error  = self.the_strings[6]
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
            self.set_display = True     # True to show the colour scalebar
            self.dpi    = 300
            self.nMode  = 0
            self.cm     = 0
            #
            self.arV    = None
            self.arL    = None
            self.ticksV = None
            self.ticksL = None
            self.vramp  = None
            self.cramp  = None
            self.fig    = None
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
                    #  draw tick every    n   values
                    msk = [True if ((offset + s) % ticksep) == 0 else False 
                                                            for s in range(len(self.arL))]
                    #  set ticks to display
                    self.ticksV = self.arV[msk]
                    self.ticksL = self.arL[msk]
                else:
                    self.ticksV = self.arV
                    self.ticksL = self.arL
            self.arV = None
            self.arL = None
            #
            # Additional parameters: default values
            self.title_align = 'center'
            self.units_align = 'center'
            self.ticks_font_properties = FontProperties()
            self.title_font_properties = FontProperties()
            self.units_font_properties = FontProperties()
            self.mathfont_set = 'cm'

            self.title_font_properties.set_family('sans-serif')
            self.title_font_properties.set_size(self.tfont)
            self.title_font_properties.set_weight('bold')

            self.units_font_properties.set_family('sans-serif')
            self.units_font_properties.set_size(self.ufont)
            self.units_font_properties.set_weight('medium')

            self.ticks_font_properties.set_family('sans-serif')
            self.ticks_font_properties.set_size(self.fntSize)
    #-------------------------------------------------------------------------------------

    def _check_font_properties(self, font, weight='normal'):
        ''' Check if the given font properties are valid. '''
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
            self.error = self.the_strings[0]
            return False
        #
        if tag.hasAttribute('version'):
            v = int(tag.getAttribute('version').strip()[0])
            if v != 3: #Version 3
                self.error = self.the_strings[1] % v
                return False
        #
        tag = dom.getElementsByTagName("rasterrenderer")[0]
        rtype = tag.getAttribute('type')
        if not tag.hasAttribute('band'):
            self.error = self.the_strings[10]
            return False            
        rband = tag.getAttribute('band')
        if int(rband) > 1:
            self.error = self.the_strings[2]
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
                self.error = self.the_strings[3]
                return False
            #
            # 1: Continuous, 2: Equal interval, 3: Quantile
            cm = int(tag.getAttribute('classificationMode'))  

        # Get original colour ramp from the dom 
        tagcr = tag.getElementsByTagName("colorramp")[0]
        try:
            tagcr = tagcr.getElementsByTagName("prop")
        except:
            # Unhandled error: probably not a qml v3.x
            self.error = self.the_strings[1]
            return False

        for p in tagcr:
            if not p.hasAttribute('k'):
                # Unhandled error: probably not a qml v3.x
                self.error = self.the_strings[1]
                return False

            if p.getAttribute('k').lower() == 'stops':
                c  = p.getAttribute('v')  # 0.02;70,8,92,255:0.04;71,16,99,255:...
                ar = c.split(':')
                n  = len(ar)
                va = np.zeros(n, np.float32)
                co = np.zeros((n, 4), np.float32)
                for i, a in enumerate(ar):
                    b = a.split(';')
                    va[i] = b[0]
                    c = b[1].split(',')
                    co[i, 0] = float(c[0]) / 255.
                    co[i, 1] = float(c[1]) / 255.
                    co[i, 2] = float(c[2]) / 255.
                    co[i, 3] = float(c[3]) / 255.
                tramp = np.zeros(n + 1, np.float32)
                for i in range(1, n):
                    tramp[i] = (va[i - 1] + va[i]) / 2.
                tramp[-1] = 1.0
                break

        # Read colour values
        items = tag.getElementsByTagName(ntag)
        n = len(items)
        if n < 2:
            self.error = self.the_strings[3]
            return False

        if nMode < 2:
            # Number of colours is one less than number of ticks
            arColo = np.zeros((n, 4), np.float32)
            arV    = np.zeros(n + 1, np.float32)
            arL    = np.array(['' * 16] * (n + 1), dtype="<U16")
            if rmin != 'min':
                arV[0] = float(rmin)
            arL[0] = self._format_label(rmin)
            ioff = 1
        else:
            arColo = np.zeros((n, 4), np.float32)
            arV    = np.zeros(n, np.float32)
            arL    = np.array(['' * 16] * n, dtype="<U16")
            ioff = 0

        # Get each colour (RGBA) and its value/label (arV/arL)
        for nC, a in enumerate(items):
            if a.hasAttribute('color'):
                colo = a.getAttribute('color')
                alph = a.getAttribute('alpha')
                valu = a.getAttribute('value')
                labl = a.getAttribute('label')
                arColo[nC, 0] = float(int(colo[1:3],16)) / 255. # red     [0, 1]
                arColo[nC, 1] = float(int(colo[3:5],16)) / 255. # green   [0, 1]
                arColo[nC, 2] = float(int(colo[5:],16)) / 255.  # blue    [0, 1]
                arColo[nC, 3] = float(alph) / 255.              # alpha   [0, 1]
                if valu == 'inf':                                 # infinity...
                    if rmax != 'rmax':
                        valu = rmax
                    else:
                        valu = '%.0f' % (2 * arV[nC - 1] - arV[nC -2] + .5)
                    labl = rmax
                arV[nC + ioff] = float(valu)                    # value (position of...)
                arL[nC + ioff] = self._format_label(labl)        # label (...what is shown)
            else:
                # Unhandled error
                self.error = self.the_strings[4]
                return False

        if rmin == 'min' and nMode < 2:
            arV[0] = '%.0f' % (2 * arV[1] - arV[2] - .5)

        # map ramp values to data values
        va = tramp * (arV[-1] - arV[0]) + arV[0]

        # Format data according to colour scheme
        #---------------------------------------

        if cm == 3:
            # Quantile: deal with badly designed colour ramp (remove colours)
            b = True
            msk = []
            for i in range(1, nC):
                if arV[i] == arV[i - 1]:
                    msk.append(i - 1)
            arV = np.delete(arV, msk)
            arL = np.delete(arL, msk)
            arColo = np.delete(arColo, msk, axis=0)
            nC = len(arV) - 1

        if nC == 1 and nMode < 2:
            # only two values: min, min, max
            # correct to: min, half, max
            if arV[0] == arV[1]:
                arV[1] = (arV[0] + arV[2]) / 2.
                arL[1] = self._format_label(arV[1])

        if nMode > 1:
            # EXACT or PALETTED
            # values = index. Colour scalebar is based on index
            # labels are what is read from file
            # Here number of colours = number of ticks
            # ticks plot in the middle of the colour box
            if cm != 3:
                v5 = 2 * arV[-1] - arV[-2]
            else:
                m = (arV[1:] - arV[:-1]).mean()
                v5 = arV[-1] + m
            va = np.hstack((arV, np.array([v5,])))
            co = arColo
            # center arV on colour, but keep arL as is
            ar = [(arV[i] + arV[i - 1]) / 2. for i in range(1, len(arV))]
            ar.append((v5 + arV[-1]) / 2.)
            arV = np.array(ar)
        #
        # Otherwise
        # ticks plot at the edge of the colour box. Number of ticks = number of colours +1
        #
        elif (cm == 1 and nC > n) or (nMode != 1):
            # use colour palette instead of the colour ramp because colour palette has
            # more colours than the colour ramp!
            co = arColo
            va = arV

        # Set colour info
        self.vramp = va
        self.cramp = co
        self.arV   = arV
        self.arL   = arL
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
        twk = 0.
        if self.ori == 'horizontal':
            xp = Length
            yp = Width
            if self.LabelsonBoth:
                labT, labB, labR, labL = True, True, False, False
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
            else:
                if self.Labelson == 'left':
                    labT, labB, labR, labL = False, False, False, True
                else:
                    labT, labB, labR, labL = False, False, True, False
        #
        self.xp, self.yp = xp, yp
        return labT, labB, labR, labL, twk
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
            self.error = self.the_strings[9]
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

    def set_extras(self, **kwargs):
        ''' Set additional parameters to control the appearance of the colour scalebar.

            kwargs:
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
        if not type(kwargs) is dict:
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
        cramp     = self.cramp
        vramp     = self.vramp
        Titre     = self.Titre.strip()
        Units     = self.Units.strip()
        cbwh      = self.cbwh
#        fntSize   = self.fntSize
        border_lw = self.border_lw
        border_cl = self.border_color
        div_lw    = self.divider_lw
        div_cl    = self.divider_color
        title_cl  = self.title_color
        units_cl  = self.units_color
        #
        labT, labB, labR, labL, twk = self._set_label_position()

        # Fonts to be used for title and units
        fontu = self.units_font_properties
        fontt = self.title_font_properties

        fig = plt.figure(dpi=self.dpi, figsize=(self.xp, self.yp), #facecolor='c', 
                         clear=True, constrained_layout=False)
        self.fig = fig

        mpl.rcParams['mathtext.fontset'] = self.mathfont_set

        # Colour scalebar axes: define and set ticks and labels
        if ori == 'horizontal':
            xmin, xmax = vramp[0], vramp[-1]
            ymin, ymax = 0., 1.
            cax = fig.add_axes([0., 0., 1., cbwh])
            cax.set_xlim([xmin, xmax])
            cax.set_ylim([ymin, ymax])
            # ticks and labels
            cax.get_yaxis().set_ticks([])
            cax.set_xticks(ticksV)
            cax.set_xticklabels(ticksL, fontproperties=self.ticks_font_properties)
            xl, yl, wl, hl = 0., .4, 1., .6
        else:
            xmin, xmax = 0., 1.
            ymin, ymax = vramp[0], vramp[-1]
            cax = fig.add_axes([0.5 - cbwh / 2., 0., cbwh, 0.8])
            cax.set_xlim([xmin, xmax])
            cax.set_ylim([ymin, ymax])
            # ticks and labels
            cax.get_xaxis().set_ticks([])
            cax.set_yticks(ticksV)
            cax.set_yticklabels(ticksL, fontproperties=self.ticks_font_properties)
            xl, yl, wl, hl = 0., 0.8, 1., 0.2

        # Other dummy axes
        clg = fig.add_axes([xl, yl, wl, hl])
        clg.get_yaxis().set_ticks([])
        clg.get_xaxis().set_ticks([])
        clg.set_axis_off()

        if not self.LabelsonBoth and self.Labelson == 'none':
            cax.set_axis_off()
        else:
            # Ticks and labels options  labelsize=fntSize, 
            cax.tick_params(bottom=labB, top=labT, left=labL,
                            right=labR, labelbottom=labB, labeltop=labT, labelleft=labL,
                            labelright=labR, width=0.4, length=2, direction='out',
                            pad=1, colors=border_cl)

        # Draw colour scalebar
        nC = len(cramp)
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

        # Plot legend
        plt.draw()
        inva = cax.transData.inverted()                            # convert to Data space

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
            ti = Titre.split('ÿ')
            for i, t in enumerate(ti[::-1]):
                ti = cax.text(xm, ym, t,
                        horizontalalignment = self.title_align,
                        verticalalignment   = 'bottom',
                        fontproperties      = fontt,
                        color               = title_cl,
                        transform           = cax.transData)
                if i == 0:
                    plt.draw()
                    tbb = ti.get_window_extent()
                    tca = inva.transform([[tbb.x0, tbb.y0],[tbb.x1, tbb.y1]])
                    tl, tb, tw, th = self._get_bounds(tca)
                ym += th * 1.15

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
            self.error = self.the_strings[5]
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
                self.error = self.the_strings[8] + '\n' + my_svg.get_error()
        else:
            self.error = my_svg.get_error()

        if self.b_png:
            # Also save a png file and crop it
            imgFileN = fil + '.png'
            self._save_png(imgFileN)

        return True
#=========================================================================================
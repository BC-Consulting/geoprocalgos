# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bc_svg
                         Trim colour scalebar svg file
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

 Manipulate SVG created by bcColorBar (matplotlib svg) to remove extra spaces 
 around the colour bar.
==========================================================================================

figure_1
 - axex_3                   if exists, delete
 - axes_2                   dummy axes: out, if no axes_3, oherwise this is alternate tick
 + axes_1
 
     text_n+1 ... text_m:   title    (m > n+1)
     text_n:                units
 
     patch_n:               top axes frame
     patch_n-1:             bottom axes frame
     patch_n-2:             right axes frame
     patch_n-3:             left axes frame

     matplotlib.axis_2:     y-axis  (empty for horizontal cb)
     matplotlib.axis_1:     x-axis  (empty for vertical cb)

     patch_3 ... patch_n-4: colour boxes
     patch_2:               axes frame

 + patch_1:                 figure frame -> out


What to do:
    - remove patch_1
    - remove axes_3 and possibly axes_2
    - unwrap axes_1 and possible axes_2
    - resize svg

path commands are:
    Absolute coords (uppercase)  -  Relatice coords (lowercase: m, l, h, v, q)
    M  : Move to (start point)        X, Y
    L  : Line to (draw to)            X, Y
    z  : Close path (draw to start)   -
    H  : Horizontal line to           X        - not used by matplotlib
    V  : Vertical line to             Y        - not used by matplotlib
    Q  : Bézier curve                 iX, iY, eX, eY   i: inflection point,  e end point
    zM : Close path and move to       X, Y

WARNING: code formatting does not follow pycodestyle recommendations
"""

import os, codecs, re
import datetime

try:
    from .utils import get_dom, get_svg_header, bc_prettify_txt
except:
    from utils import get_dom, get_svg_header, bc_prettify_txt
in_debug_mode = False
# =========================================================================================


class bc_svg():
    ''' Class to resize a svg file created with bcCBar. '''

    _dico_cmd = {}

    _the_strings = {"E_NOPARSE": "ERROR: Cannot parse the svg file!",
                    "E_NOSAVE": "ERROR: Cannot save svg to original loatation!"}

    def __init__(self, the_svg_file, the_title=''):
        ''' Initialise the process: read the svg into a dom object. '''
        #
        self.init = False
        self.the_svg_file = the_svg_file
        self.the_title = the_title
        self.__err = ''
        #
        try:
            dom = get_dom(the_svg_file)
            self.the_svg = dom.find('svg')
            self.h = self.the_svg['height']
            self.w = self.the_svg['width']
            self.version = self.the_svg['version']
            self.vb = self.the_svg['viewbox']
            self.init = True
        except:
            self.err = self._the_strings["E_NOPARSE"]
            dom = get_dom('<html><body></body></html>', btxt=True)
            #
        # Remove useless elements 
        gs = dom.find('g', {'id': 'patch_1'})
        if gs is not None:
            gs.decompose()
        a3 = dom.find('g', {'id': 'axes_3'})
        gs = dom.find('g', {'id': 'axes_2'})
        if a3 is None:
            if gs is not None:
                gs.decompose()
        else:
            a3.decompose()
            gs.unwrap()
        gs = dom.find('g', {'id': 'axes_1'})
        if gs is not None:
            gs.unwrap()
        gs = dom.find('g', {'id': 'matplotlib.axis_1'})
        if gs is not None:
            gs.unwrap()
        gs = dom.find('g', {'id': 'matplotlib.axis_2'})
        if gs is not None:
            gs.unwrap()
        gs = dom.find('g', {'id': 'matplotlib.axis_3'})
        if gs is not None:
            gs.unwrap()
    # -------------------------------------------------------------------------------------

    def _format_id(self, L):
        ''' Put the id attribute in front of all others, for paths in defs tag. '''
        #
        oattr = ''
        for a in L.attrs:
            if a == 'id':
                attr0 = L['id']
            elif a != 'clip-path':
                oattr += ' ' + a + '="' + L[a] + '"'
                if a == 'd':
                    ar = L['d'].split(' ')
                    for i in range(len(ar)):
                        if ar[i] != '' and ar[i][0] > chr(64):
                            if ar[i] not in self._dico_cmd:
                                self._dico_cmd[ar[i]] = 1
                            else:
                                self._dico_cmd[ar[i]] += 1
        return '<path id="' + attr0 + '"' + oattr + '/>'
    # -------------------------------------------------------------------------------------

    def _get_trSc(self, L):
        ''' Extract translate pair, rotate, and scale pair from string L.
            Return 2 tuples and a float: translate [x,y], scale[x,y] & rotate
        '''
        #
        # 'translate(101.035828 65.49559)rotate(-90)scale(0.05 -0.05)'
        ar = L.split(')')
        xytr = [0., 0.]
        xysc = [1., 1.]
        vrot = 0.
        for e in ar:
            if e == '':
                continue
            if 'translate' in e.lower():
                tr = e.replace('translate(', '')
                tr = tr.replace(',', ' ').replace('-', ' -').replace('  ', ' ').strip()
                tr = tr.replace('  ', ' ').strip()
                a = tr.split(' ')
                xytr = [x for x in map(float, a)]
            if 'scale' in e.lower():
                sc = e.replace('scale(', '')
                sc = sc.replace(',', ' ').replace('-', ' -').replace('  ', ' ').strip()
                sc = sc.replace('  ', ' ').strip()
                a = sc.split(' ')
                xysc = [x for x in map(float, a)]
            if 'rotate' in e.lower():
                sc = e.replace('rotate(', '')
                vrot = float(sc)
        #
        return xytr, xysc, vrot
    # -------------------------------------------------------------------------------------

    def _split_use(self, u):
        ''' Extract position info from <use>,
            can be x="", transform="" or nothing.
            Return the x attribute value and the transform attribute value. '' if absent
        '''
        #
        if u.has_attr('transform'):
            tx = ''
            tt = u['transform']
        elif u.has_attr('x'):
            tx = u['x']
            tt = ''
        else:
            tx = ''
            tt = ''
        #
        return tx, tt
    # -------------------------------------------------------------------------------------

    def _parse_path(self, p):
        ''' Parse the d element of a path (p) into its components.
            Return a list of components [['cmd', x, y, ...]]
        '''
        #
        try:
            d = p['d'].strip()
        except:
            return []

        elem = []
        cmd = []
        num = ''
        for c in d:
            if c == ' ' or c == ',' or c == '-':
                # separator
                if num != '':
                    cmd.append(num)
                if c == '-':
                    num = '-'
                else:
                    num = ''
            elif c > chr(64):
                # command
                if num != '':
                    cmd.append(num)
                elem.append(cmd)
                cmd = [c]
                num = ''
            elif c < chr(64):
                # a number
                num += c
        #
        if num != '':
            cmd.append(num)
            elem.append(cmd)
        #
        return elem
    # -------------------------------------------------------------------------------------

    def is_init(self):
        ''' Check that the class is correctly initialised.
            True if all ok
            False if error, call get_error() for more info
        '''
        #
        return self.init
    # -------------------------------------------------------------------------------------

    def get_error(self):
        ''' Return the error information. '''
        #
        return self.__err
    # -------------------------------------------------------------------------------------

    def auto_process(self):
        ''' Do all processing in one call.
            Return True on success, False otherwise (check get_error for info)
        '''
        #
        if self.__resize():
            return self.__svg_save()
        else:
            return False
    # -------------------------------------------------------------------------------------

    def __getdefs(self):
        '''Extract all defs from the dom.'''
        #
        # Three kinds of defs in the vsg: style, path and clip
        # For clip massage them to get id first
        # Finally sort all those defs
        defs = self.the_svg.find_all('defs')
        def_ar = []
        all_defs = get_svg_header()
        for c in defs:
            a = c.children
            for q in a:
                if str(q).strip() != '':
                    s = ''
                    if q.name == 'path':
                        s = self._format_id(q)
                    elif q.name != 'clippath':
                        s = str(q)
                    if s != '':
                        def_ar.append(s)
                        all_defs += s

        all_defs += '</svg>'
        dre = re.compile(r'(\d+)')
        def_ar.sort(key=lambda l:[int(s) if s.isdigit() else s.lower() 
                                                               for s in re.split(dre, l)])
        dom_defs = get_dom(all_defs, True)
        self.def_ar = def_ar
        return dom_defs
    # -------------------------------------------------------------------------------------

    def __getcbardim(self):
        '''Find dimensions of the colour bar (only, no text) => paths define rectangles.'''
        #
        self.patch1 = self.the_svg.find('g', {'id': 'figure_1'})
        pths = self.patch1.find_all('path')
        #
        xmin = 1e6
        xmax = -xmin
        ymin = xmin
        ymax = xmax
        #
        allds = []
        for pth in pths:
            del pth['clip-path']
            if pth.parent.name == 'g':
                dar = self._parse_path(pth)
                if len(dar) > 0:
                    # build the drawing commands array
                    allds += dar
        self.__err = ''
        for e in allds:
            if len(e) > 0 and e[0] in 'MLQ':
                for i, sxy in enumerate(e[1:]):
                    xy = float(sxy)
                    if (i % 2) == 0:
                        # X-ccord
                        xmin = xy if xmin > xy else xmin
                        xmax = xy if xmax < xy else xmax
                    else:
                        # Y-coord
                        ymin = xy if ymin > xy else ymin
                        ymax = xy if ymax < xy else ymax
            elif len(e) > 0 and e[0].lower() != 'z':
                self.__err += 'Not known ' + e[0]
        #
        return xmax, xmin, ymax, ymin
    # -------------------------------------------------------------------------------------

    def __resize(self):
        ''' Resize the svg: remove extra spaces. This is the main routine.
            Return True on success, False otherwise (check get_error for info)
        '''
        #
        dom_defs = self.__getdefs()
        #
        # Remove all defs, we got them already
        gs = self.the_svg.find_all('defs')
        for g in gs:
            g.decompose()
        #
        # Find dimensions of the colour bar (only, no text) => paths define rectangles
        xmax, xmin, ymax, ymin = self.__getcbardim()
        if in_debug_mode:
            print('xmin, xmax, ymin, ymax', xmin, xmax, ymin, ymax, ':::', xmax-xmin, ymax-ymin)
        #
        # Find plot dimensions. Compute max/min of texts bounding box
        texts = self.the_svg.find_all('g', {'id': re.compile(r"text_\d*")})
        for text in texts:
            #<g id="text_35">
            # <!-- $\mathcal{A}\mathrm{sin}(2 \omega t)$ -->
            # <g style="..." transform="translate(101.035828 65.49559)scale(0.05 -0.05)">
            #  <use transform="translate(0 0.015625)" xlink:href="..."></use>
            #  <use transform="translate(85.199982 0.015625)" xlink:href=""></use>
            # </g>
            #</g>
            #
            # or
            #
            #<g id="text_34">
            # <!-- Colour bar for -->
            # <g style="..." transform="translate(89.833015 51.487621)scale(0.06 -0.06)">
            #  <use xlink:href="..."></use>
            #  <use x="73.388672" xlink:href="..."></use>
            #  <use x="142.089844" xlink:href="..."></use>
            # </g>
            #</g>
            ggss = text.find_all('g')
            for gg in ggss:
                trans = gg['transform']
                xytr, xysc, vrot = self._get_trSc(trans)           # global transform for this text
                ivrot = int(abs(vrot) + .4999)
                if ivrot == 90:
                    ix = 1
                    iy = 0
                else:
                    ix = 0
                    iy = 1
                uses = gg.find_all('use')                          # all characters in this text
                x0 = 0.
                maxx = 0.
                dx = -9e9
                for use in uses:
                    if use.has_attr('transform'):                  # this character transform
                        trsc = use['transform']                    #    (translate only)
                        tr = self._get_trSc(trsc)[0]
                    else:
                        tr = [0., 0.]
                    if use.has_attr('x'):                          # or this character x-offset
                        x = float(use['x'])
                    else:
                        x = 0.
                    dx = (x - x0) if (x - x0) > dx else dx         # max character width (x)
                    maxx = x                                       # position of this character
                    x0 = x
                maxx += dx                                         # max x-distance
                if ivrot == 90:
                    Dx = 1.2 * dx * abs(xysc[1])
                    xmi = xytr[0] + tr[0] - Dx
                    xma = xytr[0] + tr[0] + Dx
                    yma = xytr[1] + tr[1]
                    ymi = yma - maxx * xysc[0]
                    if in_debug_mode:
                        print('rot=90, Dx, Dy:', Dx, maxx * xysc[0])
                else:
                    Dy = 1.2 * dx * abs(xysc[1])
                    xmi = xytr[0] + tr[0]
                    xma = xmi + maxx * xysc[0]
                    ymi = xytr[1] + tr[1] - Dy
                    yma = xytr[1] + tr[1] + Dy
                    if in_debug_mode:
                        print('rot=0, Dx, Dy:', maxx * xysc[0], Dy)
                if in_debug_mode:
                    print('scx, scy, w, dx:', xysc[0], abs(xysc[1]), maxx, dx)
                    print('TRx, TRy, trx, try', xytr[0], xytr[1], tr[0], tr[1])
                    print('xmi, xma, ymi, yma', xmi, xma, ymi, yma)
                xmin = min(xmi, xmin)
                xmax = max(xma, xmax)
                ymin = min(ymi, ymin)
                ymax = max(yma, ymax)
        # bounds
        self.w1, self.h1 = xmax - xmin, ymax - ymin
        if in_debug_mode:
            print('xmin, xmax, ymin, ymax', xmin, xmax, ymin, ymax, ':::', xmax-xmin, ymax-ymin)
        #
        # New svg dimensions and viewbox
        self.vb1 = '%0.6f %0.6f %0.6f %0.6f' % (0., 0., xmax-xmin, ymax-ymin)
        # Global translate to get the scalebar into the view box
        self.trans = 'translate(%0.6f %0.6f)' % (-xmin, -ymin)
        #
        return True
    # -------------------------------------------------------------------------------------

    def __svg_save(self):
        ''' Save the modified svg to file at original location.
            Return True on success, False otherwise (check get_error for info)
        '''
        #
        if self.the_title == '':
            titre = os.path.splitext(os.path.split(self.the_svg_file)[1])[0]
        else:
            titre = self.the_title
        final = get_svg_header().replace('BCH',  '%0.6f' % self.h1)
        final = final.replace('BCW', '%0.6f' % self.w1)
        final = final.replace('BCV', self.vb1)
        final = final.replace('BCTITRE', titre)
        final = final.replace('BCDATE', str(datetime.date.today()))
        if in_debug_mode:
            svgfile = os.path.splitext(self.the_svg_file)[0] + '___testing.svg'
        else:
            svgfile = self.the_svg_file
        try:
            with codecs.open(svgfile, 'w', 'utf-8') as fo:
                fo.write(final)
                fo.write('  <defs>\n')
                for d in self.def_ar:
                    fo.write('    %s\n' % d)
                fo.write('  </defs>\n')
                fo.write('  <g id="bcCBar" transform="%s">\n' % self.trans)

                fo.write(bc_prettify_txt(str(self.patch1)))

                fo.write('  </g>\n')
                fo.write('</svg>\n')
        except:
            self.err = self._the_strings["E_NOSAVE"]
            return False
        #
        return True


# if __name__ == '__main__':
#     in_debug_mode = True
#     filesvg = r'D:\ud\difference_20936.svg'
#     mysvg = bc_svg(filesvg, 'This is a test')
#     if mysvg.is_init():
#         err = mysvg.auto_process()
#         print(err)
#         print(mysvg.trans, mysvg.vb1)
#     else:
#         print('Cannot init parser')
#         
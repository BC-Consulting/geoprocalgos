# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bc_svg
                         Trim colour scalebar svg file
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

 Manipulate SVG created by bcColorBar (matplotlib svg) to remove extra spaces
 around the colour bar.
==============================================================================

WARNING: code formatting does not follow pycodestyle recommendations
"""

import os, codecs, re
import datetime

try:
    from .utils import get_dom, get_svg_header, bc_prettify_txt
except:
    from utils import get_dom, get_svg_header, bc_prettify_txt
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
        gs = self.the_svg.find_all('defs')
        for g in gs:
            g.decompose()
        #
        # Find dimensions of the colour bar (only, no text) => paths define rectangles
        xmax, xmin, ymax, ymin = self.__getcbardim()
        #
        # Find plot dimensions. Compute max/min of texts bounding box
        texts = self.the_svg.find_all('g', {'id': re.compile(r"text_\d*")})
        for text in texts:
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
                for use in uses:
                    if use.has_attr('transform'):                  # this character transform
                        trsc = use['transform']                    #    (translate only)
                        tr = self._get_trSc(trsc)[0]
                    else:
                        tr = [0., 0.]
                    if use.has_attr('x'):                          # or this character x-offset
                        x0 = float(use['x'])
                    else:
                        x0 = 0.
                    #
                    x = xytr[0] + (tr[0] + x0) * xysc[0]           # x position of this character
                    y = xytr[1] + tr[1] * xysc[1]                  # y position of this character
                    if ivrot == 90:
                        x, y = y, x
                    letter = use['xlink:href'][1:]                 # this character
                    dle = dom_defs.find('path', {'id': letter})    # find its definition path
                    #
                    if dle.has_attr('d'):
                        pth = self._parse_path(dle)
                        scl = self._get_trSc(dle['transform'])[1]  # transform="scale(0.015625)
                        for p in pth:                              # for each command in path def
                            if len(p) > 0 and p[0] in 'MLQ':       #  ['M', x0, y0, x1, y1, ...]
                                for i, sxy in enumerate(p[1:]):
                                    xy = float(sxy)
                                    if (((i % 2) == 0) and ivrot == 0) or (((i % 2) == 1) and ivrot == 90):
                                        # X-ccord
                                        xy = xy * scl[0] * xysc[ix] + x
                                        xmin = xy if xmin > xy else xmin
                                        xmax = xy if xmax < xy else xmax
                                    else:
                                        # Y-coord
                                        xy = xy * scl[0] * xysc[iy] + y
                                        ymin = xy if ymin > xy else ymin
                                        ymax = xy if ymax < xy else ymax
        # bounds
        self.w1, self.h1 = xmax - xmin, ymax - ymin
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
        try:
            with codecs.open(self.the_svg_file, 'w', 'utf-8') as fo:
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

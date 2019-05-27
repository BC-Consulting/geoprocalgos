# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bcCBar
                                 A QGIS plugin
 Create a colour scalebar for Composer
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

  UTILS
  Collection of small functions used on xml formatted docs

"""

import codecs
from bs4 import BeautifulSoup

def get_dom(the_file, btxt = False):
    ''' Parse a html file or a string into a dom object.
        the_file: file name if btxt is False, 
                  string in btxt is True

        return: BS4 dom object
    '''
    #
    if not btxt:
        with codecs.open(the_file, 'r', 'utf-8') as fid:
            buff = fid.read()
    else:
        buff = the_file
    #
    buff = buff.replace('\r', '').replace('\n', '')
    L = len(buff)
    while True:
        buff = buff.replace('  ', ' ')
        if len(buff) == L:
            break
        L = len(buff)
    buff = buff.replace('( ', '(')
    buff = buff.replace(' )', ')')
    buff = buff.replace(' .', '.')
    buff = buff.replace(' ]', ']')
    buff = buff.replace('[ ', '[')
    try:
        dom = BeautifulSoup(buff, 'lxml')
    except:
        raise
    #
    return dom
#-----------------------------------------------------------------------------------------

def bc_prettify_txt(sto):
    ''' Prettify a SVG document.
        sto: string representing a svg document

        return: a formatted string representing the same svg document
    '''
    #
    # de-prettify
    st = sto.replace('\r', '')
    st = st.replace('\n', '')
    st = st.replace('>', '>\n')
    st = st.replace('\n\n', '\n')
    st = st.replace('><', '>\n<')
    #
    L = len(st)
    while True:
        st = st.replace('  ', ' ')
        st = st.replace('\n <', '\n<')
        if len(st) == L:
            break
        L = len(st)
    #
    # prettify
    st = st.replace('>\n</path>', '/>')
    st = st.replace('>\n</use>', '/>')
    #
    #   indent
    ar = st.split('\n')
    sp = '    '
    st = ''
    for a in ar:
        ast = a.strip()
        st += sp
        if ast[:2] == '<g':
            sp += '  '
            st += ast + '\n'
        elif ast[:3] == '</g':
            sp = sp[:-2]
            st = st[:-2] + ast + '\n'
        else:
            st += ast + '\n'
    #
    # Try to overcome the svg-matplotlib problem...
    arst = st.split('\n')
    for i, a in enumerate(arst):
        if (('<path' in a) and ('fill:none' not in a) and ('stroke:' not in a) and
           ('fill:' in a)):
            i1 = a.find('style') + 7  # position of 1st character after: style="
            i2 = a.find('"', i1)      # position of 1st " after style="
            stroke = ''
            arstyle = a[i1:i2].split(';')
            for ass in arstyle:
                if 'fill:' in ass:
                    stroke = 'stroke:' + ass.split(':')[1] + ';'
                    break
            arstyle[-1] = stroke   # take advantage that arstyle[-1] = '' because style
                                   #  string is always terminated with ;
            arst[i] = a[:i1] + ';'.join(arstyle) + a[i2:]  # reconstruct string
    #
    return '\n'.join(arst)
#-----------------------------------------------------------------------------------------

def get_svg_header():
    ''' SVG header for a bcCBar object. '''
    #
    return '''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<!-- Created with bcCBar from matplotlib (https://matplotlib.org/) -->
<svg xmlns:dc="http://purl.org/dc/elements/1.1/" 
     xmlns:cc="http://creativecommons.org/ns#" 
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:svg="http://www.w3.org/2000/svg"
     xmlns="http://www.w3.org/2000/svg"
     height="BCHpt"
     width="BCWpt"
     viewBox="BCV"
     version="1.1">
  <metadata id="metadata2">
    <rdf:RDF>
      <rdf:Description>
        <dc:description>
          Colour scalebar generated from a one-band raster in QGIS V3.x processing framework. SVG file to be used in QGIS Composer as a legend item to inform the raster it relates to.
        </dc:description>
        <dc:date>BCDATE</dc:date>
        <dc:creator>GeoProc.com</dc:creator>
        <dc:publisher rdf:resource="https://github.com/BC-Consulting/bccscbar3" />
      </rdf:Description>
      <cc:Work rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title>BCTITRE</dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
'''
#=========================================================================================
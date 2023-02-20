# -*- coding: utf-8 -*-
"""
General QGIS utility functions

@author: benoit
        begin                : 2019-05-19
        copyright            : (C) 2019-2023 by GeoProc.com
        email                : info@geoproc.com
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
import os
import codecs
import re
import numpy as np
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsColorRampShader as qRS,
                       QgsSingleBandPseudoColorRenderer,
                       QgsRasterShader,
                       QgsMapLayer,
                       QgsProcessingUtils)

tmpDir = QgsProcessingUtils.tempFolder()

def check_oneband(F):
    ''' Check that the given layer (F) is a one-band raster. '''
    #
    if F is None or F.type() != QgsMapLayer.RasterLayer:
        return False
    elif F.rasterType() > 0:
        return False
    else:
        return True
#=========================================================================================

def check_color(col):
    ''' Check that col can be interpreted as a colour.
        Return col if ok, 'black' on error.
    '''
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
#=========================================================================================

def check_qml_sidecar(the_layer):
    ''' Check is a qml side-car exist for the raster.
        Return the qml filename if it does, False if no sidecar.
    '''
    #
    qml = os.path.splitext(the_layer.source())[0] + '.qml'
    if os.path.exists(qml):
        return qml
    else:
        return False
#=========================================================================================

def get_dict(dic):
    ''' Create and return a dictionary for a dict-like string. One-level only.
        Any dict-like string as value of top level key is kept as is.
        All keys are returned in lowercase. All values are returned as string.
    '''
    #
    dic = dic.strip()
    if dic == '' or dic[0] != '{' or dic[-1] != '}':
        return {}
    n1, n2 = dic.count('{'), dic.count('}')
    if n1 != n2:
        return {}
    #
    q = ''.join([str(c) for c in dic])
    q = re.sub(r',\s*', ',', q)
    q = q[1:-1].replace('"', '').replace("'","")
    if n1 == 1:
        q = q.split(',')
        return {kv.split(':')[0].lower():kv.split(':')[1] for kv in q if kv != ''}
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
        a = {kv.split(':')[0].lower():kv.split(':')[1] for kv in q if kv != ''}
        for ka in a:
            for k in ar:
                if k in a[ka]:
                    a[ka] = a[ka].replace(k, ar[k])
        return a
#=========================================================================================

def style_raster(ar, the_layer):
    ''' Style a raster layer (the_layer) with an array of colours (ar)
        ar => [V, r,g,b,a]  V: raster value for the given colour (r,g,b,a)
                            V in raster unit. (r,g,b,a) [0-255]
    '''
    #
    fcn = qRS()
    fcn.setColorRampType(qRS.Interpolated)
    lst = []
    for e in ar:
        lst.append(qRS.ColorRampItem(e[0],QColor(int(e[1]), int(e[2]), int(e[3]),
                                                 int(e[4])),str(e[0])))
    fcn.setColorRampItemList(lst)
    try:
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(fcn)
        renderer = QgsSingleBandPseudoColorRenderer(the_layer.dataProvider(), 
                                                    1, shader)
        the_layer.setRenderer(renderer)
        the_layer.triggerRepaint()
    except:
        pass
    #
    return True
#=========================================================================================

def save_colormap(ar, output_file):
    ''' Save an array of colours (ar) to a QGIS colour ramp file (output_file. 
        ar => [V, r,g,b,a]  V: raster value for the given colour (r,g,b,a)
                            V in raster unit. (r,g,b,a) [0-255]
    '''
    #
    try:
        with codecs.open(output_file, 'w', 'utf-8') as fo:
            fo.write('# bcclr2tbl Generated Color Map Export File\n')
            fo.write('INTERPOLATION:INTERPOLATED\n')
            # 614,46,124,228,255,614
            for e in ar:
                fo.write('%.3f,%d,%d,%d,%d,%.1f\n' % (e[0], int(e[1]), int(e[2]),
                                                      int(e[3]), int(e[4]), e[0]))
        return True
    except:
        return False
#=========================================================================================

def save_qml(the_layer, sidecar = False):
    ''' Save the layer style to a qml file.
          sidecar: boolean
                   False: save to Processing temp directory
                   True: svce as sidecar in raster directory
        Return the filename on success, '' on failure.
    '''
    #
    if not sidecar:
        theFile = the_layer.name().split("|")[0] + ".qml"
        tempname = os.path.join(tmpDir, theFile)
        _, flg = the_layer.saveNamedStyle( tempname )
        if flg:
            return tempname
        else:
            return ''
    else:
        #                         path/to/file/layerName.ext|layername:layerName
        theFile  = os.path.splitext(the_layer.source())[0] + ".qml"
        _, flg   = the_layer.saveNamedStyle(theFile)
        #
        return flg
#=========================================================================================

qml_G = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis minScale="1e+08" hasScaleBasedVisibilityFlag="0" maxScale="0" styleCategories="AllStyleCategories" version="3.4.8-Madeira">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <customproperties>
    <property key="WMSBackgroundLayer" value="false"/>
    <property key="WMSPublishDataSourceUrl" value="false"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="identify/format" value="Value"/>
  </customproperties>
  <pipe>
    <rasterrenderer grayBand="1" gradient="BlackToWhite" type="singlebandgray" alphaBand="-1" opacity="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>MinMax</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <contrastEnhancement>
        <minValue>0</minValue>
        <maxValue>1</maxValue>
        <algorithm>StretchToMinimumMaximum</algorithm>
      </contrastEnhancement>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeBlue="128" colorizeOn="0" colorizeStrength="100" colorizeGreen="128" saturation="0" colorizeRed="255" grayscaleMode="0"/>
    <rasterresampler zoomedOutResampler="bilinear" maxOversampling="2" zoomedInResampler="bilinear"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
"""

qml_H = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis minScale="1e+08" version="3.4.7-Madeira" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" maxScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>0</Searchable>
  </flags>
  <customproperties>
    <property value="false" key="WMSBackgroundLayer"/>
    <property value="false" key="WMSPublishDataSourceUrl"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property value="Value" key="identify/format"/>
  </customproperties>
  <pipe>
    <rasterrenderer classificationMin="BCMIN" classificationMax="BCMAX" opacity="BCOPACITY" band="1" type="singlebandpseudocolor" alphaBand="-1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Exact</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader clip="0" classificationMode="1" colorRampType="INTERPOLATED">
          <colorramp name="[source]" type="gradient">
            <prop k="color1" v="BCR1,BCG1,BCB1,BCA1"/>
            <prop k="color2" v="BCR2,BCG2,BCB2,BCA2"/>
            <prop k="discrete" v="0"/>
            <prop k="rampType" v="gradient"/>
            <prop k="stops" v="BCRAMP"/>
          </colorramp>
"""

qml_E = """</colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeRed="255" colorizeOn="0" colorizeBlue="128" grayscaleMode="0" colorizeGreen="128" saturation="0" colorizeStrength="100"/>
    <rasterresampler zoomedOutResampler="bilinear" maxOversampling="2" zoomedInResampler="bilinear"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
"""

qml_c = '          <item value="BCVAL" label="BCVAL" color="BCCOLX" alpha="BCALPHA"/>'
#=========================================================================================

def to_int255(v):
    ''' Convert a number [0-1] to [0-255] '''
    #
    return int(v*255+.5) if not np.isnan(v) else 0
#=========================================================================================

def to_hex(c):
    ''' Convert a colour quadruplet into an hex string. '''
    #
    if np.isnan(c).any():
        return '#000000'
    #
    if type(c[0]) is np.float64:
        r = hex(to_int255(c[0]))[2:]
        g = hex(to_int255(c[1]))[2:]
        b = hex(to_int255(c[2]))[2:]
    else:
        r = hex(c[0])[2:]
        g = hex(c[1])[2:]
        b = hex(c[2])[2:]
    #
    return '#%s%s%s' % (('00'+r)[-2:],('00'+g)[-2:],('00'+b)[-2:])
#=========================================================================================
    
def _qml_colorramp(cramp):
    ''' Build the string for qml <colorramp> k="stops". '''
    #
    vc = np.linspace(0., 1., len(cramp), np.float(32))
    bcramp = ''
    #0.25;254,217,142,255:
    for i, q in enumerate(cramp[1:-1]):
        bcramp += '%.3f;%d,%d,%d,%d:' % (vc[i+1], to_int255(q[0]), to_int255(q[1]),
                                                  to_int255(q[2]), to_int255(q[3]),)
    #
    return bcramp[:-1]
#=========================================================================================

def write_qml(V, cramp, F, opacity = '1', grey = False):
    ''' Create a qml file from info given.
        V: numpy array of values
        cramp: list of rgba quadruplets
        F: qml filename
        opacity: colour map transparency, [0., 1.]
                  0.: fully transparent, 1.: fully opaque. Default: 1.
        grey: True to save B&W qml for sunshaded grid. False otherwise

        Return: True is qml successfuly written to disk, False otherwise.
    ''' 
    #
    if grey:
        try:
            with codecs.open(F, 'w', 'utf-8') as fo:
                fo.write(qml_G)
            return True
        except:
            return False
    #------------------------------------------------------------------

    head = qml_H.replace('BCMIN',str(V[0])).replace('BCMAX',str(V[-1]))
    head = head.replace('BCR1',str(to_int255(cramp[0][0])))
    head = head.replace('BCG1',str(to_int255(cramp[0][1])))
    head = head.replace('BCB1',str(to_int255(cramp[0][2])))
    head = head.replace('BCA1',str(to_int255(cramp[0][3])))
    head = head.replace('BCR2',str(to_int255(cramp[-1][0])))
    head = head.replace('BCG2',str(to_int255(cramp[-1][1])))
    head = head.replace('BCB2',str(to_int255(cramp[-1][2])))
    head = head.replace('BCA2',str(to_int255(cramp[-1][3])))
    head = head.replace('BCRAMP', _qml_colorramp(cramp))
    head = head.replace('BCOPACITY', opacity)

    L = ''
    n = len(cramp) - 1
    d = V[-1] - V[0]
    va = np.linspace(V[0], V[-1], n)
    for v in va:
        i = int(((v - V[0]) / d) * n + 0.5)
        q = qml_c.replace('BCVAL', str(v)).replace('BCALPHA', str(to_int255(cramp[i][3])))
        q = q.replace('BCCOLX', to_hex(cramp[i]))
        L += q + '\n'
    #
    try:
        with codecs.open(F, 'w', 'utf-8') as fo:
            fo.write(head)
            fo.write(L)
            fo.write(qml_E)
        # Extra sidecar for bcCBar3
        with codecs.open(F+'i', 'w', 'utf-8') as fo:
            fo.write('%s\n' % '\n'.join(map(str, list(V))))
        return True
    except:
        return False
#=========================================================================================

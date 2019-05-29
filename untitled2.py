# -*- coding: utf-8 -*-
"""
Created on Tue May 28 17:04:13 2019

@author: benoi
"""

import os
from math import sin, cos, radians, sqrt
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from qgis.core import QgsPoint

def rotate_line(line, cenrot, deg = -90, raw = True):
    """ Rotate self.polylines the given angle about their centers.
        line:   object to rotate:
                if raw is True line is a np.array with at least 2 columns
                if raw is False line is a QgsLineString object
        cenrot: point of rotation: QgsPoint object
        deg:    angle of rotation in degrees, positive counterclockwise from East

        Return: the rotated line in its original type

        Adapted from: https://stackoverflow.com/questions/14842090
    """
    #
    theta = radians(deg)  # Convert angle from degrees to radians
    cosang, sinang = cos(theta), sin(theta)
    cx, cy = cenrot.x(), cenrot.y()

    def doRotate(x, y):
        # Rotate each point around the point of rotation
        tx, ty = x - cx, y - cy
        px = tx * cosang - ty * sinang + cx
        py = tx * sinang + ty * cosang + cy
        return px, py

    if raw:
        for i, pt in enumerate(line):
            x, y = pt[0], pt[1]
            px, py = doRotate(x, y)
            line[i, 0] = px
            line[i, 1] = py
    else:
        for i in range(line.numPoints):
            x, y = line.xAt(i), line.yAt(i)
            px, py = doRotate(x, y)
            line.setXAt(i, px)
            line.setXAt(i, py)
    #
    return line
#=========================================================================================

def do_profile(ar, inv, scale, offset):
    ''' Create profile for current line ar. '''
    #
    nar = np.array(ar[['X','Y']])
    line_pts = [QgsPoint(x,y) for x,y in nar]

    # Rotate line to horizontal
    aziN   = line_pts[0].azimuth(line_pts[-1]) # angle positive clockwise from North
    azi    = -(aziN - 90.)
    cx, cy = nar[0, 0], nar[0, 1]              # center of rotation

    theta  = radians(-azi)
    co, si = cos(theta), sin(theta)
    tx, ty = nar[:,0] - cx, nar[:,1] - cy
    px = tx * co - ty * si + cx
    py = tx * si + ty * co + cy

    # Change Y-coords to data
    TL = abs(ar.X[0] - ar.X[len(ar)-1])  # length of the longest line
    mn = py.mean()                       # average Y-coord
    dmin = ar.Data.min()                 # minimum data value
    mult = TL / (ar.Data.max() - dmin)   # scaling factor
    offset = 0.
    scale = 1

    # New Y-coord = scaled data
    ar['Yb'] = scale * (ar.Data - dmin) * mult + offset + mn
    plt.plot(px, py, px, ar.Yb)

    # Rotate line back to original angle
    theta  = radians(azi)
    co, si = cos(theta), sin(theta)
    tx, ty = px - cx, np.array(ar.Yb) - cy
    px1 = tx * co - ty * si + cx
    ar.Yb = tx * si + ty * co + cy
    #
    return ar, px1
#=========================================================================================

angle = 75.

## Create test lines
#n = 200
#x = np.linspace(100000., 105000., n)
#y = np.linspace(1210000., 1212000., 100)
#
#with open(r'e:\test'+str(angle)+'.csv', 'w') as fo:
#    fo.write('X,Y,FID,Line,data\n')
#    fid = 0
#    line = 90
#    for ey in y:
#        cline = np.zeros([n,5],np.float32)
#        line += 10
#        v = np.random.rand(n) * 10000.
#        for i, ex in enumerate(x):
#            fid +=1
#            cline[i] = [ex, ey, fid, line, v[i]]
#        # rotate line
#        c = QgsPoint((cline[0, 0] + cline[-1, 0]) / 2., (cline[0, 1] + cline[-1, 1]) / 2.)
#        cline = rotate_line(cline, c, angle, True)
#        # save line
#        for pt in cline:
#            fo.write('%.2f,%.2f,%d,%d,%.2f\n' % (pt[0], pt[1], int(pt[2]), int(pt[3]),
#                                                 pt[4]))
##=========================================================================================


arc = []
with open(r'e:\test'+str(angle)+'.csv', 'r') as fo:
    i = 0
    while True:
        li = fo.readline()
        li = li[:-1]
        if i > 0:
            b = li.split(',')
            if i == 1:
                idl = b[3]
            elif b[3] != idl:
                break
            arc.append([float(b[0]), float(b[1]), int(b[2]), b[3], float(b[4])])
        i += 1

ar = pd.DataFrame.from_records(arc, columns=['X','Y','FID','Line','Data'])
ar = ar.sort_values('FID')

inv = False
scale = 1.
offset = 0.

ar, px = do_profile(ar, inv, scale, offset)

plt.plot(ar.X, ar.Y, px, ar.Yb)
plt.legend()

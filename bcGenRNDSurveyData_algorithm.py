# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bcGenRNDSurveyData3
                           A QGIS Processing algorithm
                       Generate dummy survey data with spikes

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
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
WARNING: code formatting does not follow pycodestyle recommendations
"""

__author__ = 'GeoProc.com'
__date__ = '2019-05-19'
__copyright__ = '(C) 2019-2023 by GeoProc.com'
__revision__ = '$Format:%H$'

import os
from math import sin, cos, radians
try:
    import numpy as np
    is_dependencies_satisfied = True
except:
    is_dependencies_satisfied = False

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProcessingAlgorithm, QgsProcessing,
                       QgsProcessingUtils,
                       QgsField,
                       QgsFields,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsPoint,
                       QgsWkbTypes,
                       QgsProcessingException,
                       QgsFeatureSink)

from .setparams import set_param
from .HelpbcA import help_bcGeneS

#-----------------------------------------------------------------------------------------
plugin_path = os.path.dirname(__file__)

the_url = 'https://www.geoproc.com/be/bcGenRNDSurveyData3.htm'
help_string = help_bcGeneS
the_tags = ['random','survey','data','noise','spike','orientation','line','tie']
#-----------------------------------------------------------------------------------------

class bcGenRNDSurveyDataAlgorithm(QgsProcessingAlgorithm):
    ''' Processing wrapper. '''
    #
    NLINES    = 'NLINES'
    NPOINTS   = 'NPOINTS'
    EXTENT    = 'EXTENT'
    ANGLE     = 'ANGLE'
    DMIN      = 'DMIN'
    DMAX      = 'DMAX'
    CRS       = 'CRS'
    DEP       = 'DEP'
    OUTPUT    = 'OUTPUT'

    _default_output = 'dummy_survey_pt'

    _ico = 'bcGenRNDSurveyData'
    _the_strings = {"ALGONAME":"Random Survey Data",
                    "ERR":"ERROR",
                    "ERR_DEP":"Some dependencies are required to run this algorithm",
                    "DEP_LST":"numpy",
                    "ERR_VECTOR":"ERROR: Input is not a vector!",
                   }

    _pstr = ["Number of lines in the dummy survey",                             # 0
             "Number of data points along each line",                           # 1
             "Survey extent",                                                   # 2
             "Line direction (in degrees, +'ve CCW from East)",                 # 3
             "Data minimum",                                                    # 4
             "Data maximum",                                                    # 5
             "CRS of the output survey (MUST be a projected crs. NO Lat/Lon)",  # 6     
             "Survey layer"]                                                    # 7

    def __init__(self):
        super().__init__()
    #-------------------------------------------------------------------------------------

    def _define_params(self):
        ''' Define parameters needed. '''
        #
        #       [0] < 100  : "normal" parameter
        # 100 < [0] < 1000 : Advanced Parameter
        #       [0] > 1000 : Output parameter
        self.the_params = {
           self.NLINES:       [1,self._pstr[0],'NumberI',
                              {'defaultValue':50,'minValue':1,'maxValue':5000},True],
           self.NPOINTS:      [2,self._pstr[1],'NumberI',
                              {'defaultValue':200,'minValue':10,'maxValue':1e5},True],
           self.EXTENT:       [3,self._pstr[2],'EXTENT',{},True],
           self.ANGLE:        [4,self._pstr[3],'NumberD',
                              {'defaultValue':0.,'minValue':-360.,'maxValue':360.},True],
           self.DMIN:         [5,self._pstr[4],'NumberD',
                              {'defaultValue':2.8e4,'minValue':-9e9,'maxValue':9e9},True],
           self.DMAX:         [6,self._pstr[5],'NumberD',
                              {'defaultValue':3e4,'minValue':-9e9,'maxValue':9e9},True],
           self.CRS:          [7,self._pstr[6],'CRS',{'defaultValue':'ProjectCrs'},True],
           self.OUTPUT:       [1001,self._pstr[7],'SINK',
                              {'type':QgsProcessing.TypeVectorPoint},True]
        }
        self._err_param = {self.DEP: [1,self._the_strings["ERR_DEP"],'String',
                           {'defaultValue':self._the_strings["DEP_LST"]},False]}
    #-------------------------------------------------------------------------------------

    def _rotate_line(self, line, cenrot, deg = -90):
        """ Rotate self.polylines the given angle about their centers.
            line:   object to rotate:
            cenrot: point of rotation: QgsPoint object
            deg:    angle of rotation in degrees, positive counterclockwise from East
    
            Return: the rotated line in its original type
        """
        #
        theta  = radians(deg)
        co, si = cos(theta), sin(theta)
        cx, cy = cenrot.x(), cenrot.y()
        #
        tx, ty = line[:, 0] - cx, line[:, 1] - cy
        line[:, 0] = tx * co - ty * si + cx
        line[:, 1] = tx * si + ty * co + cy
        #
        return line
    #-------------------------------------------------------------------------------------

    def _noise(self, n, dd, per):
        ''' Generae noise. 
            n:   number of points in array
            dd:  data amplitude
            per: percentage of noise over dd
    
            Return: centered noise array
        '''
        #
        p = dd * per / 100.
        return p * (np.random.rand(n) - 0.5)
    #-------------------------------------------------------------------------------------
    
    def _spike(self, n):
        ''' Generate spikes.
            n: number of points in array
    
            Return: array with random spikes (+/-5, +/-10 or +/15 times base level)
        '''
        #
        ar = np.zeros(n, dtype=np.float32)
        rd = np.random.rand(n)

        def seed_s():
            s = float(np.random.rand(1))
            if s < 0.01:
                s = 6.072
            elif s < 0.0618:
                s = 3.236
            elif s < 0.985:
                s = 0.
            elif s < 0.995:
                s = 4.554
            else:
                s = 9.708
            return s

        npo = len(ar[(rd>0.95)])
        nne = len(ar[(rd<0.05)])
        ar[(rd>0.95)] = [ seed_s() / 1.618 for i in range(npo)]
        ar[(rd<0.05)] = [-seed_s() / 1.618 for i in range(nne)]
        return ar
    #-------------------------------------------------------------------------------------

    def initAlgorithm(self, config):
        ''' Here we define the inputs and output of the algorithm. '''
        #
        self._define_params()
        if is_dependencies_satisfied:
            # Prepare all parameters needed
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

        self.tmpDir = QgsProcessingUtils.tempFolder()
        self._error = ''
    #-------------------------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        ''' Here is where the processing itself takes place. '''
        #
        if not is_dependencies_satisfied:
            return {}

        nL    = self.parameterAsInt(parameters, self.NLINES, context)
        n     = self.parameterAsInt(parameters, self.NPOINTS, context)
        angle = self.parameterAsDouble(parameters, self.ANGLE, context)
        Dmin  = self.parameterAsDouble(parameters, self.DMIN, context)
        Dmax  = self.parameterAsDouble(parameters, self.DMAX, context)
        crs   = self.parameterAsCrs(parameters, self.CRS, context)
        bbox  = self.parameterAsExtent(parameters, self.EXTENT, context, crs)

        xmin  = bbox.xMinimum()
        xmax  = bbox.xMaximum()
        ymin  = bbox.yMinimum()
        ymax  = bbox.yMaximum()

        # Set output vector layer
        output_wkb = QgsWkbTypes.Point
        fields = QgsFields()
        fields.append(QgsField('X', QVariant.Double, '', 24, 16))
        fields.append(QgsField('Y', QVariant.Double, '', 24, 16))
        fields.append(QgsField('FID', QVariant.Int, '', 12, 0))
        fields.append(QgsField('Line', QVariant.String, '', 12))
        fields.append(QgsField('Data', QVariant.Double, '', 24, 16))
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields,
                                               output_wkb, crs)
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Create test lines
        dx = (xmax - xmin) / n                       # point separation
        dy = (ymax - ymin) / nL                      # line separation
        # lines - no noise
        x0  = np.linspace(xmin, xmax, n+1)           # points along line
        y0  = np.linspace(ymin, ymax, nL+1)          # lines Y-coords
        # Ties - no noise
        nT = int((xmax - xmin) / (dy * 10) + 0.5)
        npT = int((ymax - ymin) / dx)
        x1 = np.linspace(xmin, xmax, nT+1)           # tie-lines X-coords
        y1 = np.linspace(ymin, ymax, npT+1)          # points along tie-lines
        # Adjust to real stuff
        n   += 1
        nL  += 1
        nT  += 1
        npT += 1
        # Data - no noise
        w  = np.linspace(-2 * np.pi, 4 * np.pi, n)
        wT = np.linspace(-6 * np.pi, 6 * np.pi, npT)
        # Data - with noise
        Vs = []
        Dd = Dmax - Dmin
        d = 0.01 * (np.sin(w) + np.cos(w)) * Dd + Dmin
        n2 = int(n/2)
        if (n % 2) == 0:
            off = 0
        else:
            off = 1
        d += np.hstack((np.array([i/2. for i in range(n2)]), 
                        np.array([(n2-i)/2. for i in range(n2+off)])))
        for i in range(int(nL / 10)+1):
            if (i % 3) == 0:
                V = d + self._noise(n, Dd, 3.)
                V = (V + np.roll(V,1) + np.roll(V,2) + np.roll(V,3) + np.roll(V,4)) / 5.
                V += 0.05 * self._spike(n) * Dd
            elif (i % 4) == 0:
                V = d + self._noise(n, Dd, 3.)
                V = (V + np.roll(V,1) + np.roll(V,2) + np.roll(V,3) + np.roll(V,4)) / 5.
                V += 0.5 * self._spike(n) * Dd
            else:
                V = d + self._noise(n, Dd, 3.)
                V = (V + np.roll(V,1) + np.roll(V,2) + np.roll(V,3) + np.roll(V,4)) / 5.
                V += 0.1 * self._spike(n) * Dd
            Vs.append(V)
        Vs[1] = np.roll(Vs[1], 6)
        VTs = []
        for i in range(nT):
            VT = 0.01*(np.sin(wT) + np.cos(wT))*Dd/3. + self._noise(npT, Dd, 50.) + Dmin
            VT = (VT + np.roll(VT,1) + np.roll(VT,2) + np.roll(VT,3) + np.roll(VT,4)) / 5.
            VT = (VT + np.roll(VT,1) + np.roll(VT,2) + np.roll(VT,3) + np.roll(VT,4)) / 5.
            VT = (VT + np.roll(VT,1) + np.roll(VT,2) + np.roll(VT,3) + np.roll(VT,4)) / 5.
            VTs.append(VT)

        # Y-coords with noise: line offset
        y0 = y0 + self._noise(nL, dy, 10.)
        x1 = x1 + self._noise(nT, dy, 10.)

        # Generate survey
        fid = 0
        line = 90
        total = 90. / nL
        f = QgsFeature()
        for j in range(nL):
            if feedback.isCanceled():
                break

            line += 10
            k = int(j / 10)
            # Add noise on point location
            x = x0 + self._noise(n, dx, 3.)
            if k == 0:
                aV = np.roll(Vs[k], abs(int((j+1)**.95)))
            elif k == 1:
                aV = np.roll(Vs[k], -abs(int((j+1-10)**.95)))
            else: aV = Vs[k]
            cline = np.array([[ex, y0[j] + float(self._noise(1, dy, 3.)), fid + i + 1,
                                                  line, aV[i]] for i, ex in enumerate(x)])
            fid += n
            if k == 0:
                np.roll(Vs[k], 3)

            # rotate line
            if j == 0:
                # define centre of rotation
                c = QgsPoint(cline[0, 0], cline[0, 1])
            cline = self._rotate_line(cline, c, angle)
            # reverse line if odd
            if (j % 2) == 1:
                cline[:,0] = cline[:,0][::-1]
                cline[:,1] = cline[:,1][::-1]
                cline[:,4] = cline[:,4][::-1]
            # save line
            for pt in cline:
                f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(pt[0], pt[1])))
                f.setAttributes([float(pt[0]),float(pt[1]),int(pt[2]),str(pt[3]),
                                 float(pt[4])])
                sink.addFeature(f, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(j * total))

        # Tie lines
        line = 10090
        total = 10. / nT
        for j in range(nT):
            if feedback.isCanceled():
                break

            line += 10
            # Add noise on point location
            yT = y1 + self._noise(npT, dx, 3.)
            cline0 = np.array([[x1[j] + float(self._noise(1, dy, 3.)), ey, fid + i + 1,
                                             line, VTs[j][i]] for i, ey in enumerate(yT)])
            fid += nL
            # rotate line
            cline = self._rotate_line(cline0, c, angle)
            # reverse line if odd
            if (j % 2) == 1:
                cline[:,0] = cline[:,0][::-1]
                cline[:,1] = cline[:,1][::-1]
                cline[:,4] = cline[:,4][::-1]
            # save line and add to data frame
            for pt in cline:
                f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(pt[0], pt[1])))
                f.setAttributes([float(pt[0]),float(pt[1]),int(pt[2]),str(pt[3]),
                                 float(pt[4])])
                sink.addFeature(f, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(j * total) + 90.)

        return {self.OUTPUT:dest_id}
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
        return 'bcGenRNDSurveyData3'
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
        One of: composer, layer, raster, survey, vector
        '''
        return 'survey'
    #-------------------------------------------------------------------------------------

    def tr(self, string):
        ''' No translation of strings. '''
        #
        return string
    #-------------------------------------------------------------------------------------

    def createInstance(self):
        ''' Creates a new instance of the algorithm class. '''
        #
        return bcGenRNDSurveyDataAlgorithm()
    #-------------------------------------------------------------------------------------
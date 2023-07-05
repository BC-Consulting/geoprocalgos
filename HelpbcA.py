# -*- coding: utf-8 -*-
"""
       Help strings for GeoProcAlgos algorithms

Convention to be used:
    - variable name must be: help_bcAlgorithmName (no 3 as suffix)
    - long description must be given in the first line.
    - all parameters must be described
    - all paramater description must start with * <b>

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

### help_bcSaveqml
help_bcSaveqml = """
Save the style of each selected layer in .qml files.
* <b>Input QGIS vector layers</b> [optional]: Click the button to select vector layers for which .qml file will be created.
* <b>Input QGIS raster layers</b> [optional]: Click the button to select raster layers for which .qml file will be created.
* <b>Result file</b>: a html file that shows results. Leave as is.<br/>
The qml filename has the same name as the layer and it is located in the same directory.<br/>
For more information see the <a href="https://www.geoproc.com/be/bcSaveqml3.htm">home page</a>.
"""

### help_bcStackP
help_bcStackP = """Creates 2D stacked profiles for survey data along lines and tie lines.

<b>Base parameters</b>
* <b>Input vector</b> [required]: Must be a point layer having the following fields: Fiducial, Line number and data.
* <b>Fiducial field</b> [required]: Fiducial are unique number increasing monotonically over all the data points. It is used to sort the lines by increasing coordinates.
* <b>Line field</b> [required]: Line number field in order to sort the stacked profiles correctly.
* <b>Data field</b> [required]: The field from which the stacked profiles are generated. Must be a numeric field.
* <b>Dummy value</b> [optional]: Value for invalid or missing data. Default: 9999.00.
* <b>Inverse profiles?</b> [optional]: By default, stacked profiles are displayed above the line to which they relate. Check that option to display profiles below their lines. Note that this depends on the azimuth of the first line found in the layer. If it is positive the default is to plot profiles on top of the line. If the azimuth is negative, the profiles will be displyed below the line by default.
* <b>Profile scale</b> [optional]: Stacked profiles data need to be scaled to display properly. Mainly because the unit of the data is generally not the units used for the coordinates. Here, the scale factor is the ratio of data amplitude over the length of the longest line. You will have to experiment to find the correct value. Note that the default value (3) would generally be far too much. A 0.3 value could be just good!
* <b>Profile offset</b> [optional]: This is the distance between line and profile. Experiment to arrive at something meaningfull! 0. is the default, but it does not mean that the profile is display on the line!
* <b>Join profile to line?</b> [optional]: By default profiles are "floating" over the lines. Check this option to link profiles ends to lines ends. This can be visually nicer!!
* <b>Output</b> [optional]: The line vector layer created by the algorithm. See below.<br/>

<b>Advanced parameters</b>
* <b>Scale profile relative to another channel?</b>: If you want to compare profiles from different channels in your layer you can then check 'Do scaling relative to another channel?' and select the channel used for scaling the profiles. Default is False.
* <b>Scaling layer</b>: If the previous option is checked, select the layer that has the channel to use for scaling. This is generally the same has the input layer. So re-select the input layer here. The reason you have to re-select the layer is that you could create stacked profiles from a sub-set (selection) of the input layer and want to scale over the entire layer's data. Default: unused.
* <b>Scaling channel</b>: If the previous option is checked, then select the channel to exctract the information from. Default: unused.<br/>

<b>Results</b>
Resulting line vector (LineM geometry) has the following fields:
- <i><b>Line</b></i>: storing the original line number. Its coordinates are derived from the data channel used.
- <i><b>Type</b></i>: line type, either L or T for line and tie-line, respectively.
- <i><b>NbPts</b></i>: number of points in the profile.
- <i><b>Azimuth</b></i>: azimuth of the line. Positive clockwise from North.
- <i><b>DistEP</b></i>: distance between end points of the line.
- <i><b>Length</b></i>: length of the line (&ge; DistEP).
- Coordinates: X,Y,M where M is data value.
"""

### help_bcDispGeom
help_bcDispGeom = """
"""

### help_bcGeneS
help_bcGeneS = """Generate dummy survey data with spikes
Survey consists of x many lines of any orientation and y many tie lines perpendicular to the lines.
Data is a periodic signal between -1. and 1. which has noise and spikes added to it.
Noise is also introduced into the X- and Y-coords of lines and tie lines.
"""

### help_bcSwapYZ
help_bcSwapYZ = """Create a 3D vector layer by swapping Y & Z coords.
Z does not exist in original layer, so that Y is constant for all features!.<br/>

* <b>Input vector</b> [required]: layer to transform geomtries.
* <b>Y value</b> [optional]: New Y-value. Default: 0.
* <b>Output vector file</b> [optional]: resulting 3D layer. The z-component is added and is equal to old Y.
"""

### help_bcclr2tbl
help_bcclr2tbl = """Style a raster with a GoldenSoftware Surfer .clr file (Version 3).
.clr files can be generic Surfer files with no customisation, or a .clr file tuned-up to the raster of interest.<br/>

* <b>Input raster</b> [required]: Raster to the styled with the .clr.
* <b>clr file</b> [required]: Surfer .clr file to style the input raster with.
* <b>Output</b> [optional]: Converted QGIS colour map file in output.
"""

### help_bcMultiStyles
help_bcMultiStyles = """Load and save all layer's styles from/to qml files.<br/>
qml files should have the following format (i.e. sidecar):
<b>layerName_styleName.qml</b>
Where: <em>layerName</em> is the same name as the layer the qml relates to.
<em>styleName</em> is the name of the style given in Style Manager.<br/>

* <b>Input layer</b> [required]: The layer to act on.
* <b>Save</b> [required]: Save all styles in different qml files. Default False, implying a load operation.
* <b>Do not use layer name as prefix</b>: If True try to load all qml's from directory, or save qmls without layer name prefix. If False, load only layer's qml sidecars, or save as sidecars i.e. with layer name as a prefix.
* <b>qml Directory</b> [optional]: Directory to load/save qml from/to.  By default the directory containing the layer will be used.<br/>
* <b>Output Result file</b> [optional]: A HTML file showing the results of the operation. Leave empty to save to Layer source directory.<br/>

If <em>Save</em> is True each layer's style is saved to its own qml.
If <em>Save</em> is False (default) qml's are read from files and added to the layer's Style Manager.
If <em>Do not use layer name as prefix</em> is False when loading, only sidecar qml's following the above naming convention are loaded. Otherwise all qml's in the directory are loaded, if possible.  
If <em>Do not use layer name as prefix</em> is False when saving, sidecar qml's are created (i.e. the style name is prefixed by the layer name).  Otherwise qml's are named using only the style name.

<b>NOTE</b>
If one of the styles is named 's', then there is a problem! This is because the algorithm is created for geophysics workflows where the suffix '_s' is appended to sunshaded grid of product of the same name.
"""

### help_bcInterpies4QGIS
help_bcInterpies4QGIS = """ "<em>A libray for the interpretation of gravity and magnetic data.</em>"
Interpies includes filtering of geophysical grids and, in its native form, display of processed grids.
In this port to QGIS, the viewing of data is done through QGIS interface using Interpies graphics elements.<br/>
All units in SI system. Other units will give wrong results!<br/>

* <b>Input layer</b> [required]: One-band raster layer to act on.
* <b>Detrend?</b> [optional]: True to detrend layer before filtering. Default: False.
* <b>Filter</b> [required]: Name of the filter to apply from filters list. Default: First Vertical Derivative.
* <b>Filter parameters</b> [optional]: Python dictionary-like string of filters parameters. Default: None.
* <b>Colour map</b> [optional]: Colour map used to render filtered layer. Default: cet_rainbow.
* <b>Colour distribution mode</b> [optional]: Type of normalisation of the colormap. Select from list. Default: Equalise.
* <b>Colourbar ticks distribution</b> [optional]: How colourbar ticks are spaced. Select fromm list. Default: Linear.
* <b>Ouptut contours?</b> [optional]: True to output a contour line vector file. Default: False.
* <b>Number of contours or array or definition</b> [optional]: If above is True, define the number of contours (Default 32), or give a list of contour values '[100, 120, ...]' or give a contour step starting with ">|" notation. E.g. '>5|300' will draw contours every 5 values from 300 value.
* <b>Generate sunshaded layer?</b> [optional]: True to created a sunshaded layer, give its name below. Default: False.
* <b>Sunshading parameters</b> [optional]: Sun azimuth [0, 180], Sun elevation [0, 90], alpha [0, 1] and cell [1, 100] . Default: 45,45,0.5,50.
* <b>Output: Sunshaded layer</b> [optional]: Name of sunshaded file if 'Output sunshaded layer?' is True.
* <b>Output: Filtered layer</b> [optional]: Resulting filtered layer.<br/>

Use batch mode to compute more than one filter at once.<br/>

Current filters:
 - Copy: Return a non-filtered copy of the input grid. Used for colouring the original grid, or to return the detrended grid, if "Detrend?" is True.
 - 1VD: first vertical derivative. Parameters {'dz_method':ZMETHOD, kwargs}.
 - VD: vertical derivative. Parameters {'order':n, 'dz_method':ZMETHOD,kwargs}.
 - dX: Horizontal gradient in X-direction. Parameters {'hgm_method':METHOD, dargs3, kwargs}.
 - dY: Horizontal gradient in Y-direction. Parameters {'hgm_method':METHOD, dargs3, kwargs}.
 - dXdY: Second horizontal gradients. Parameters {'hgm_method':METHOD, dargs3, kwargs}.
 - dX2, dY2: Second horizontal gradients. Parameters {'hgm_method':METHOD, dargs4, kwargs}.
 - HGM: Horizontal gradient magnitude or Total Horizontal Derivative. Parameters {'hgm_method':METHOD, dargs3, kwargs}.
 - Total Derivative. Parameters {'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs3, kwargs}.
 - Standard directional derivative. Parameters {'azimuth':0., 'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs3, kwargs}.
 - VI: Vertical integral. Parameters {'order':1, 'eps':1e-6, kwargs}.
 - Up: Upward continuation. Parameter {'Z':500, kwargs} in cell size units.
 - Down: Downward continuation. Parameter {'Z':500, kwargs} in cell size units.
 - RTP: Reduction-to-pole. Parameters {'inclination':45, 'declination':0, kwargs}. Be aware of blow-outs near magnetic equator, and leakage over large surveys.
 - RTP-GC: Reduction-to-pole with G. Cooper's algo. Parameters {'inclination':45, 'declination':0, kwargs}. Be aware of blow-outs near magnetic equator, and leakage over large surveys.
 - VRTP: Variable Reduction-to-Pole. Parameters {'inc':filename of 2D array of inclinations, 'declination':0, kwargs}.
 - AS (same as TGA): Analytic signal. Parameters {'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs3, kwargs}.
 - TGA: Total gradient amplitude (same as AS). Parameters {'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs3, kwargs}.
 - TA: Tilt angle. Parameters {'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs3, kwargs}.
 - TA2: 2<sup>nd</sup> order tilt angle. Parameters {'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs3, kwargs}.
 - TAHG: Tilt angle of the horizontal gradient. Parameters {'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs4, kwargs}.
 - Hyperbolic tilt angle. Parameters {'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs3, kwargs}.
 - Downward continuation of TA. Parameters {'alpha':1, 'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs3, kwargs}.<br/> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; alpha implements the downward continuation of the tilt angle.
 - Tilt Based Directional Derivative. Parameters {'azimuth':0., 'hgm_method':METHOD, dargs3, kwargs}.
 - HP: High-pass filter. Apply a high-pass filter by subtracting an upward continued version of the data. Parameter {'Z':5000, kwargs} in cell size units.
 - Smoothing filters. Parameters {'sigma':1, 'method':'SG|gaussian', 'deg':3, 'win':5, 'doEdges':False}.
 - Laplacian: Laplacian using 2D convolution.Parameters None.
 - LW: Local wavenumber. Parameters {'hgm_method':METHOD, 'dz_method':ZMETHOD, dargs4, kwargs}.
METHOD is one of: 'SG'*, 'FS' or 'fourier'.<br/>&nbsp;&nbsp;&nbsp;&nbsp;SG: use Savitzky-Golay coeficients to compute derivative.<br/>&nbsp;&nbsp;&nbsp;&nbsp;FS: use Farid and Simoncelli coeficients to compute derivative.<br/>&nbsp;&nbsp;&nbsp;&nbsp;fourier: use FFT to compute derivative.
ZMETHOD is one of: 'isvd'* or 'fourier'.<br/>&nbsp;&nbsp;&nbsp;&nbsp;isvd: use integrated second vertical derivative method to compute derivative.<br/>&nbsp;&nbsp;&nbsp;&nbsp;fourier: use FFT to compute derivative.
kwargs:<br/>&nbsp;&nbsp;&nbsp;&nbsp;{ padding:'full*|3x3|pow2', mode:'reflect*|linear_ramp', reflect_type:'odd*|even' }
dargs3:<br/>&nbsp;&nbsp;&nbsp;&nbsp;{ 'deg':3, 'win':5, 'fs_tap':5*|7, 'doEdges':True*|False, ncells:2 }
dargs4:<br/>&nbsp;&nbsp;&nbsp;&nbsp;{ 'deg':4, 'win':5, 'fs_tap':5*|7, 'doEdges':True*|False, ncells:2 }
<b>*</b>: <em>default</em>
<dl>
 <dt>deg: positive integer. Defaults to 3 or 4 depending of selected filter.</dt>
  <dd>The degree of the Savitzky-Golay filter if the SG method is used.</dd>
 <dt>win: positive odd integer, default 5.</dt>
  <dd>The size of the fitting window that is used to calculate the SG coefficients.</dd>
 <dt>fs_tap: 5 or 7, default 5.</dt>
  <dd>Size of the kernel that is used to calculate the derivatives with the FS method.</dd>
 <dt>doEdges: boolean, default True</dt>
  <dd>Replace the values at the edges of the output array with values calculated by reflection padding. Useful to correct bad edge effects.</dd>
 <dt>ncells: int, default: 2</dt>
  <dd>Number of cells at the edges of the output grid that are replaced using padding if the `doEdges` option is True.</dd>
 <dt>padding: string</dt>
  <dd>Type of padding to apply to the input grid before the Fourier calculation.<br/>Can be one of the following options:<br/>&nbsp;&nbsp;&nbsp;'full': initial 3x3 padding (reflect) + ramp or reflection to next power of 2<br/>&nbsp;&nbsp;&nbsp;'3x3': The entire array is duplicated and tiled in a 3x3 pattern with the original array in the middle.<br/>&nbsp;&nbsp;&nbsp;'pow2': the size of the array is increased by padding to the next power of 2.</dd>
 <dt>mode: string, default: 'reflect'</dt>
  <dd>Option for padding the input array.<br/>&nbsp;&nbsp;&nbsp;'reflect': Pads with the reflection of the array<br/>&nbsp;&nbsp;&nbsp;'linear_ramp': Pads with a linear ramp between the array edge value and the mean value of the array.</dd>
 <dt>reflect_type: string, default: 'odd'</dt>
  <dd>Used in reflection padding. Can be 'even' or 'odd'.</dd>
</dl>

Colour map names are all matplotlib legal names plus: cet_rainbow (as defined by Peter Kovesi's rainbow_bgyr_35_85_c73), geosoft or clra128, clra32, clrb128, elevation, pastel, resis (those 6 from Geosoft .tbl files), parula (from matlab), win256 (as used for colour quantisation with pillow).<br/>

<b>At the end of the processing, please see the report file. It contains useful information about the grid and has the radially averaged power spectrum image and data.<b><br/>

<b>Copyright notices</b>:
Interpies from Josepth Barraud distributed under BSD 3-Clause License.
RTP-GC and VRTP adapted from Gordon Cooper.
Please see report for licence info.
"""

### help_bcigrf
help_bcigrf = """Compute IGRF values from input locations.
Time range is 1900 to 2020, with extension to 2025 with degraded accuracy.
All units in SI system. Other units will give wrong results!<br/>

Input must be a point vector layer.
Output will be another point layer with the following fields (some optional, dependant on selected options):
Longitude (°), Latitude (°), Date (YYYY-MM-DD), FID, Altitude (m), TMI (nT), IGRF (nT), IGRF_Declination (°), IGRF_Inclination (°), IGRF_NS-component (nT), IGRF_EW-component (nT), IGRF_Z-component (nT), TMI-IGRF (nT).
Z and TMI can be from 'z' and 'm' coordinates respectively instead of from fields. But they are also optional.
The layer's crs is converted to Lat/Lon WGS84 if not already in that crs.<br/>

<b>PARAMETERS</b>
* <b>Input point layer</b> [required]: name of the input layer.
* <b>Survey date (Format YYYY-MM-DD)</b> [optional]: Date the data was acquired.
* <b>or Date channel</b> [optional]: Date channel if no date is provided above.
* <b>Date format</b> [optional]: Date format in python datetime tokens (e.g. %Y for YYYY, %m for MM and %d for DD). If date is numeric AND is in Julian day then this field must be blank. If date is numeric AND NOT in Julian day, data format must be YYYYMMDD.0.
* <b>FID channel</b></b> [optional]: Fiducial channel, in order to compare with original points.
* <b>Z channel from z-coord?</b> [optional]: True if the Z values are to be raken from z-coord. Default: False.
* <b>or Z channel</b> [optional]: if above is False, define the field holding the Z-coordinates.
* <b>or Survey altitude</b> [optional]: If there is no Z-channel in the data, provide an mean elevation.
* <b>TMI channel</b> [optional]: Define the field holding the TMI values.
* <b>Substract IGRF from TMI?</b> [optional]: True to add field (TMI channel must be defined). Default: False.
* <b>Add mean data value back?</b> [optional]: Add the average TMI value to the TMI-IGRF difference to get range compatible TMI. Default: True.
* <b>Output file name</b> [optional]: Output vector file name with computed IGRF parameters, and TMI-IGRF, if enabled.

<b><em>WARNING</em></b>: Results take some time to compute. Results given here should be very close to results given by NOAA <a href="https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml#igrfwmm">Magnetic Field Calculators</a> (IGRF Model).
"""

### help_bcigrfraster
help_bcigrfraster = """Compute IGRF values from input locations.
Time range is 1900 to 2020, with extension to 2025 with degraded accuracy.
All units in SI system. Other units will give wrong results!<br/>

Input must be a oneband raster layer.
An IGRF grid, the same size as the original raster, is the output. Optionally, a grid of TMI-IGRF can be created and the specialised incv grid can also be created (see bcInterpies4QGIS for its use in var-RTP).
The layer's crs is converted to Lat/Lon WGS84 if not already in that crs.<br/>

<b>PARAMETERS</b>
* <b>Input layer</b> [required]: name of the oneband raster layer to process.
* <b>Survey date (Format YYYY-MM-DD)</b> [required]: Date the data was acquired.
* <b>Survey altitude</b> [Required]: Mean survey elevation, in metres. Default: 1000. m.
* <b>Substract IGRF from value?</b> [optional]: True to create the output layer as: TMI - IGRF instead of just: IGRF values. Default: True.
* <b>Add mean data value back?</b> [optional]: If above is True, and this is True then add the average data value to the TMI - IGRF difference to get values compatible to TMI. Default: True.
* <b>Create an inclination raster grid? (For variable reduction to the pole)</b> [optional]: If you want to compute the variable reduction to the pole with Interpies4QGIS you need this grid. Default: False.
* <b>File name of inc grid</b> [optional]: file name to store the raster values of the IGRF inclination at each point.
* <b>Output file name</b> [optional]: a raster file to store the computed IGRF total intensity values in nanoTesla (nT).

<b><em>WARNING</em></b>: Results take some time to compute. Results given here should be very close to results given by NOAA <a href="https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml#igrfwmm">Magnetic Field Calculators</a> (IGRF Model).
"""

### help_bcMAT2TIF
help_bcMAT2TIF = """Convert a Matlab .mat file version 6 to a geoTIFF file.<br/>

<b>PARAMETERS</b>
* <b>Input mat file</b> [required]: Name of Matlab .mat file version 6 to convert.
* <b>Extent (xmin, xmax, ymin, ymax)</b> [required]: lower/left - upper/right bounds.
* <b>Cell separation (X-sep, Y-sep)</b> [required]: cell separation.
* <b>No data value</b> [optional]: the no data value in the .mat file. Default: -99999.
* <b>crs</b> [required]: reference system the data is in.
* <b>Output geotif</b> [optional]: output geoTIFF filename.

<b>Copyright notices</b>:
Interpies from Josepth Barraud distributed under BSD 3-Clause License.
"""

### help_bcLenDir
help_bcLenDir = """Fill fields length and direction from simple line geometries and save to new vector layer.<br/>

The input layer must be an existing single part line vector layer. Furthermore, that layer must have two numeric fields to be filled with length and direction values. A copy of the original vector is created.
If a multi-parts layer is input then only the first part is processed. All remaining parts are disregarded.
If '<i>Selected features only</i>' is selected, output layer will only have the selected features from input vector.<br/>

Note: angle 0 degree is pointing North. 90 degrees is pointing East, ...<br/>

<b>PARAMETERS</b>
* <b>Input layer</b> [required]: name of the line vector layer to process.
* <b>Length field</b> [required]: field to store line lengths, must exist and be numeric.
* <b>Direction field</b> [required]: field to store line directions, must exist and be numeric.
* <b>Orientation method</b> [optional]:
&nbsp;&nbsp;&nbsp;&nbsp;- How to compute orientation: Orientation of the longest segment of the line (default), or,
&nbsp;&nbsp;&nbsp;&nbsp;- Average orientation from all segments in line, weighted by segment length, or,
&nbsp;&nbsp;&nbsp;&nbsp;- Orientation from end points only.
* <b>direction neutral</b> [optional]: Should lines in opposite directions be handled as having the same direction. Default, True (result in angles between [0 and 180[ degrees only).
* <b>Output file name</b> [optional]: a line vector file to store the computed lengths and directions.
 """

### help_bcSunshade
help_bcSunshade = """Sunshading of a grid<br/>
Do the sunshading after reading a grid from file, then save to sunshaded file(s) in the same diretory as the input file.
The 4 sunshading parameters are lists so that the algorithm loops over all possible combinations and output as many sunshaded grids as needed.<br/>

<b>PARAMETERS</b>
* <b>Filename</b> [required]: name of the grid file to be sunshaded.
* <b>Sun azimuths</b> [optional]: Sun azimuth values: start, stop, step. (In range [-180, 180] degrees). Default: 45&deg;,,
* <b>Sun elevation</b> [optional]: Sun elevation along azimuth: start, stop, step. (In range [0, 90] degrees). Default: 45&deg;,,
* <b>alpha</b> [optional]: How much incident light is reflected (wetness): start, stop, step. (In range [0, 1]). Default: 0.5,,
* <b>cell</b> [optional]: How compact the bright patch is ("relief" exaggeration): start, stop, step. (In range [1, 100]). Default: 50,,
* <b>Nodata value</b> [optional]: Value of nodata in grid. Default: None, read it from grid file.
* <b>Smooth sunshaded grid</b> [optional]: Select to have the sunshaded grid smoothed. Default: not selected.

Output format:
List of filenames of the saved sunshaded grids built as follows:
name-of-the-grid__shAZI_ELEV_ALPHA_CELL.tif
&nbsp;&nbsp;&nbsp;&nbsp;AZI: value for sun azimuth
&nbsp;&nbsp;&nbsp;&nbsp;ELEV: value for sun elevation
&nbsp;&nbsp;&nbsp;&nbsp;ALPHA: value for alpha
&nbsp;&nbsp;&nbsp;&nbsp;CELL: value for cell

<b>Copyright notices</b>:<br>&nbsp;&nbsp;&nbsp;Patrick Cole: Flexible Sunsdading in Python. <a href="https://github.com/softwareunderground/notebooks">Link</a><br>&nbsp;&nbsp;&nbsp;Interpies from Josepth Barraud distributed under BSD 3-Clause License.
"""

### help_bcCMap
help_bcCMap = """Create a colour map for the given one-band raster using a colour ramp and a normalisation function.<br/>

<b>PARAMETERS</b>
* <b>Input one-band raster</b> [required]: Layer to use for computing the colour map.
* <b>Colour ramp to use</b> [optional]: Name of colour ramp from list. Default: i_cet_rainbow.
* <b>Colour normalisation</b> [optional]: See below. Select from list. Default: Equalise.
* <b>Number of colours</b> [optional]: Number of colours in the colour map. Default: 256. Only valid for 'equalise' and 'autolevels'. If normalisation is 'none' then the number of colours is the number of colours in the selected colour ramp.
* <b>Minimum percent</b> [optional]: Only if 'Colour normalisation' is "autolevels". Minimum percentage of data to use.
* <b>Maximum percent</b> [optional]: Only if 'Colour normalisation' is "autolevels". Maximum percentage of data to use.
* <b>Brightness</b>: [optional]: Apply a brightness filter [0., 10.] to colour map. < 1 for darkening, > 1 for brightening. Default: 1.0 (no filter).
* <b>Output colour map file</b> [optional]: Name of the file storing the created colour map. Default: full-input-raster-name_colour-ramp-name.txt

<dl>
Type of normalisation of the colormap are:
 <dt>'equalise'</dt>
  <dd>Increases contrast by distributing intensities across all the possible colours. The distribution is calculated from the data and applied to the colormap.</dd>
 <dt>'autolevels'</dt>
  <dd>Stretches the histogram of the colormap so that dark colours become darker and the bright colours become brighter. The extreme values are calculated with percentiles: min_percent (defaults to 2%) and max_percent (defaults to 98%).</dd>
 <dt>'none'</dt>
  <dd>The colormap is not normalised. The data can still be normalised in the usual way using the 'norm' keyword argument and a Normalization instance defined in matplotlib.colors().</dd>
</dl>

<b>Copyright notices</b>:<br>&nbsp;&nbsp;&nbsp;Interpies from Josepth Barraud distributed under BSD 3-Clause License.
"""

### help_bcASEGgdf
help_bcASEGgdf = '''A simple wrapper around <b>asg_gdf2</b> to import an ASEG-GDF file into a point layer.<br/>

<b>PARAMETERS</b>
* <b>Input ASEG-GDF file</b> [required]: Full path to the .dfn ASEG-GDF sidecar file to read.
* <b>Output point layer name</b> [optional]: Name of the imported layer/file.

<b>Copyright notices</b>:<br>&nbsp;&nbsp;&nbsp;asg_gdf2 python module by <a href="https://github.com/kinverarity1/aseg_gdf2">kinverarity1</a> under MIT Licence.
'''

### help_bcFPPL
help_bcFPPL = '''Generate a series of parallel lines over a given rectangular area.<br>

The rectangular area must cover the area of interest (a polygon vector) which is also provided as a parameter.<br>

<b>PARAMETERS</b>
* <b>Input area vector (polygon)</b> [required]: Area to draw parallel lines on.
* <b>Box coordinates [LL-UR]</b> [required]: A North-South box enclosing the area of interest.
* <b>Line separation</b> [required]: Distance between each consecutive line. Default: 50.
* <b>Line orientation (degrees)</b> [required]: Direction of the lines (positive East from North). Default: 0.
* <b>First Line Number</b> [optional]: The id number of the first line.
* <b>Line offset</b> [optional]: X-offset and Y-offset of the first line from the box coordinates. Default: (0,0).
* <b>Output line vector file</b> [optional]: Flight path over the area of interest. Line vector.

Note:<br>&nbsp;&nbsp;&nbsp;Line number MUST be numbers. They increas from left to right. If line numbers must increase from right to left then use a negative number equal to the largest expected line number.

The line vector layer has the following fields:<br>&nbsp;&nbsp;&nbsp;X0: X-coord of start point<br>&nbsp;&nbsp;&nbsp;Y0: Y-coord of start point<br>&nbsp;&nbsp;&nbsp;X1: X-coord of end point<br>&nbsp;&nbsp;&nbsp;Y1: Y-coord of end point<br>&nbsp;&nbsp;&nbsp;XC: X-coord of line centroid<br>&nbsp;&nbsp;&nbsp;YC: Y-coord of line centroid<br>&nbsp;&nbsp;&nbsp;DX1: XC - X0<br>&nbsp;&nbsp;&nbsp;DY1: YC - Y0<br>&nbsp;&nbsp;&nbsp;DX2: XC - X1<br>&nbsp;&nbsp;&nbsp;DY2: YC - Y1<br>&nbsp;&nbsp;&nbsp;Length: Line length<br>&nbsp;&nbsp;&nbsp;Direction: Line orientation (constant)<br>&nbsp;&nbsp;&nbsp;Line: Line number<br>&nbsp;&nbsp;&nbsp;LineType: Line type (constant)<br>&nbsp;&nbsp;&nbsp;LineSep: Line separation (constant)
'''

### help_bcFPStats
help_bcFPStats = '''Generate statistics for a flight path layer.<br>

<b>PARAMETERS</b>
* <b>Input area vector (line)</b> [required]: Flight path layer.
* <b>Output</b> [optional]: Statistics file.

<b>Reported statistics are:</b><br>&nbsp;&nbsp;&nbsp;- Number of lines<br>&nbsp;&nbsp;&nbsp;- Line spacing (km)<br>&nbsp;&nbsp;&nbsp;- Line direction (deg)<br>&nbsp;&nbsp;&nbsp;- Total length (km)<br>&nbsp;&nbsp;&nbsp;- Average length (km)
Length of each Line:<br>&nbsp;&nbsp;&nbsp;- Line number, Length
Line Info:<br>&nbsp;&nbsp;&nbsp;- Line_number, Xstart, Ystart, Xend, Yend, Xcentroid, Ycentroid, XdistCS, YdistCS, XdistCE YdistCE, Length, Direction
'''

### help_bcFP
help_bcFP = '''Generate a flight path layer and a fiducials/stations layer over an area of interest (AoI).<br>

First generate parallel lines over a rectangular area that must cover the AoI (a polygon vector) which is also provided as a parameter. Then clip the lines aver the AoI and compute some statistics. Finally generate a point layer representing fiducials/stations along the lines.<br>

Uses a combination of 4 algorithms:<br>&nbsp;&nbsp;&nbsp;- bcFPPL3: to create parallel lines over a larger rectangular area.<br>&nbsp;&nbsp;&nbsp;- clip: to clip the parallel lines over the area of interest.<br>&nbsp;&nbsp;&nbsp;- bcFPStats3: to create the statistics file over the AoI.<br>&nbsp;&nbsp;&nbsp;- bcFPPT3: to generate the points layer.

<b>PARAMETERS</b>
* <b>Input area vector (polygon)</b> [required]: Area to draw parallel lines on.
* <b>Box coordinates [LL-UR]</b> [required]: A North-South box enclosing the area of interest.
* <b>Line separation</b> [required]: Distance between each consecutive line. Default: 50.
* <b>Line orientation (degrees)</b> [required]: Direction of the lines (positive East from North). Default: 0.
* <b>First Line Number</b> [optional]: The id number of the first line.
* <b>Line offset</b> [optional]: X-offset and Y-offset of the first line from the box coordinates. Default: (0,0).
* <b>Fiducial/sample separation</b> [required]: Point separation along each line. Default: 100.
* <b>Fiducial/sample offset</b> [required]: Offset of first point from start of line. Default: 0.
* <b>Output line vector file</b> [optional]: Flight path over the area of interest. Line vector.
* <b>Output</b> [optional]: Statistics file.

Note:<br>&nbsp;&nbsp;&nbsp;- Line number MUST be numbers. They increas from left to right. If line numbers must increase from right to left then use a negative number equal to the largest expected line number.<br>&nbsp;&nbsp;&nbsp;- The CRS of the area of interest is used to create the parallel lines. No check done on extent. It is assumed that extent CRS is the same as AoI CRS.

The line vector layer has the following fields:<br>&nbsp;&nbsp;&nbsp;X0: X-coord of start point<br>&nbsp;&nbsp;&nbsp;Y0: Y-coord of start point<br>&nbsp;&nbsp;&nbsp;X1: X-coord of end point<br>&nbsp;&nbsp;&nbsp;Y1: Y-coord of end point<br>&nbsp;&nbsp;&nbsp;XC: X-coord of line centroid<br>&nbsp;&nbsp;&nbsp;YC: Y-coord of line centroid<br>&nbsp;&nbsp;&nbsp;DX1: XC - X0<br>&nbsp;&nbsp;&nbsp;DY1: YC - Y0<br>&nbsp;&nbsp;&nbsp;DX2: XC - X1<br>&nbsp;&nbsp;&nbsp;DY2: YC - Y1<br>&nbsp;&nbsp;&nbsp;Length: Line length<br>&nbsp;&nbsp;&nbsp;Direction: Line orientation (constant)<br>&nbsp;&nbsp;&nbsp;Line: Line number<br>&nbsp;&nbsp;&nbsp;LineType: Line type (constant)<br>&nbsp;&nbsp;&nbsp;LineSep: Line separation (constant)

<b>Reported statistics are:</b><br>&nbsp;&nbsp;&nbsp;- Number of lines<br>&nbsp;&nbsp;&nbsp;- Line spacing (km)<br>&nbsp;&nbsp;&nbsp;- Line direction (deg)<br>&nbsp;&nbsp;&nbsp;- Total length (km)<br>&nbsp;&nbsp;&nbsp;- Average length (km)
Length of each Line:<br>&nbsp;&nbsp;&nbsp;- Line number, Length
Line Info:<br>&nbsp;&nbsp;&nbsp;- Line_number, Xstart, Ystart, Xend, Yend, Xcentroid, Ycentroid, XdistCS, YdistCS, XdistCE YdistCE, Length, Direction

<b>Copyright notices</b>:<br>&nbsp;&nbsp;&nbsp;LocatePoint algorithm (C) 2018 by Łukasz Dębek [Locate points along lines QGIS plugin].
'''

### help_bcFPPT
help_bcFPPT = '''Locate points along lines.<br>

<b>PARAMETERS</b>
* <b>Input flight path (line vector)</b> [required]: Line layer used to generate points.
* <b>Fiducial/sample separation</b> [required]: Point separation along each line. Default: 100.
* <b>Fiducial/sample offset</b> [required]: Offset of first point from start of line. Default: 0.
* <b>Output point vector file</b> [optional]: Resulting layer with all points.

<b>Copyright notices</b>:<br>&nbsp;&nbsp;&nbsp;LocatePoint algorithm (C) 2018 by Łukasz Dębek [Locate points along lines QGIS plugin].
'''

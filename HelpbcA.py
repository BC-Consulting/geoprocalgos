# -*- coding: utf-8 -*-
"""
       Help strings for GeoProcAlgos algorithms

Created on Mon Jun 3 2019
@author: benoit
"""

help_bcCBar = """
<i>Generate a colour scalebar from a one-band raster for use in Composer</i>
Paramaters needed to draw the scalebar are:
<b>Required</b>
* <b>Input</b>: currently selected raster in QGIS legend. A qml file will automatically be created.<br/>

<b>Optional</b>
* <b>Scalebar orientation</b>: "vertical"* or "horizontal"
* <b>Number of decimals</b> to display in tick labels (default: 2)
* <b>Title</b> of the colour scalebar. Use ÿ (ASCII 255) as multilines marker.
* <b>Sub-title</b> of the colour scalebar (single line). Generally units of the raster.
* <b>Ratio</b> width of the colour scalebar relative to full length (0.1)
* <b>Tick separation</b>: every 'ticksep' is shown (default: 1 [>= 1])
* <b>Offset</b> to arrive at nice numbers for ticks labelling (default: 0. [-100., 100.])
* <b>Alternate ticks on both axis?</b> False*. If True, sets 'Label both sides' to False.
* <b>Label both sides</b> of the colour scalebar or not. False*, or
* <b>Which side to label</b>: 'none', 'both', 'top', 'bottom'*, 'right'*, 'left'.
* <b>Ticks label font size</b> relative to plot area. Default 4, [.2, 10.]
* <b>Title font size</b> relative to ticks label font size (+2)* [-10.,10.]
* <b>Sub-title font size</b> relative to ticks label font size (+1)*
* <b>Colour scalebar frame line width</b> (default 1.0 [0.0, 5.0])
* <b>Colour dividers line width</b>, between colours (default 0.0 [0., 2.5])
* <b>Title colour</b> ('black'*)
* <b>Sub-title colour</b> ('black'*)
* <b>Frame colour</b> ('black'*)
* <b>Divider colour</b> ('black'*)
* <b>The scalebar can be reversed</b>. False*
* <b>A png</b> file can be created in addition to the svg file. False*
* <b>Additional parameters</b> can be defined. See home page for more details.<br/>

* <b>Ouptut</b>: the name of the svg (and png) file(s) representing the generated colour scalebar. A html file is also created that shows the colour scalebar(s) and options used. Click the link in "Result Viewer" to display it in your browser.
---
(*): default<br/><br/>

-------------------------------------------------------------------
One-band-rasters saved with QGIS V3.x are the only ones accepted.
Colour interpolation can be: LINEAR, EXACT, DISCRETE or PALETTED.
Colour mode can be: Continuous, Equal Interval or Quantile.<br/>

Title and sub-title accept text formatted in Maptplotlib mathtext.
-------------------------------------------------------------------
"""

help_bcSaveqml = """
Save the style of each selected layer in .qml files.
* <b>Input QGIS vector layers</b> [optional]: Click the button to select vector layers for which .qml file will be created.
* <b>Input QGIS raster layers</b> [optional]: Click the button to select raster layers for which .qml file will be created.
* <b>Result file</b>: a html file that shows results. Leave as is.<br/>
The qml filename has the same name as the layer and it is located in the same directory.<br/>
For more information see the home page.
"""

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

help_bcDispGeom = """
"""

help_bcGeneS = """Generate dummy survey data with spikes
Survey consists of x many lines of any orientation and y many tie lines perpendicular to the lines.
Data is a periodic signal between -1. and 1. which has noise and spikes added to it.
Noise is also introduced into the X- and Y-coords of lines and tie lines.
"""

help_bcSwapYZ = """Create a 3D vector layer by swapping Y & Z coords.
Z does not exist in original layer, so that Y is constant for all features!.<br/>

* <b>Input vector</b> [required]: layer to transform geomtries.
* <b>Y value</b> [optional]: New Y-value. Default: 0.
* <b>Output vector file</b> [optional]: resulting 3D layer. The z-component is added and is equal to old Y.
"""

help_bcclr2tbl = """Style a raster with a GoldenSoftware Surfer .clr file (Version 3).
.clr files can be generic Surfer files with no customisation, or a .clr file tuned-up to the raster of interest.<br/>

* <b>Input raster</b> [required]: Raster to the styled with the .clr.
* <b>clr file</b> [required]: Surfer .clr file to style the input raster with.
* <b>Output</b> [optional]: Converted QGIS colour map file in output.
"""

help_bcMultiStyles = """Load and save all layer's styles from/to qml files.<br/>
qml files should have the following format (i.e. sidecar):
<b>layerName_styleName.qml</b>
Where: <em>layerName</em> is the same name as the layer the qml relates to.
<em>styleName</em> is the name of the style given in Style Manager.<br/>

* <b>Input layer</b> [required]: The layer to act on.
* <b>Save</b> [required]: Save all styles in different qml files. Default False, implying a load operation.
* <b>Force load</b>: If True try to load all qml's from directory. If False, load layer's qml sidecars. No effect if Save is True.
* <b>qml Directory</b> [required]: Directory to load/save qml from/to.<br/>
* <b>Output Result file</b> [optional]: A HTML file showing the results of the operation. Leave empty to save to Layer source directory.<br/>

If <em>Save</em> is True each layer's style is saved to its own qml.
If <em>Save</em> is False (default) qml's are read from files and added to the layer's Style Manager.
If <em>Force load</em> is False, only sidecar qml's following the above naming convention are loaded. Otherwise all qml's in the directory are loaded, if possible.
 """
 
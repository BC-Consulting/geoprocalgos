<h1><img src="http://www.geoproc.com/be/img/geoproc.png" width="48" height="48" align="absmiddle" />&nbsp;&nbsp;&nbsp;&nbsp;geoprocAlgos</h1>
<p>A collection of <a href="https://qgis.org/en/site/" target="_blank">QGIS</a> V3.x Processing algorithms.</p>

<p><img src="http://www.geoproc.com/be/img/bcCbar.png" width="48" height="48" align="absmiddle" />&nbsp;&nbsp;&nbsp;&nbsp;<strong>bcCBar<sup>3</sup></strong>: Generate a coulour scalebar from a one-band raster. For use as legend in QGIS Composer.</p>
<blockquote>
  <blockquote>
    <blockquote>
      <blockquote>
         <p>QGIS version 3.x (not compatible with versions &le; 2).<br />
         Requires external python modules (numpy, matplotlib, beautifulsoup &amp; lxml)<br />
         Description page <a href="http://www.geoproc.com/be/bccbar3.htm">here</a>.</p>
      </blockquote>
    </blockquote>
  </blockquote>
</blockquote>

<p><img src="http://www.geoproc.com/be/img/bcSaveqml.png" width="48" height="48" align="absmiddle" />&nbsp;&nbsp;&nbsp;&nbsp;<strong>bcSaveqml<sup>3</sup></strong>: Save a style file (.qml) for all selected vector and raster layers. The style file is saved as a <a href="https://en.wikipedia.org/wiki/Sidecar_file" target="_blank">sidecar</a> in the same directory of the layer file.</p>
<blockquote>
  <blockquote>
    <blockquote>
      <blockquote>
        <p>QGIS version 3.x (not compatible with versions &le; 2).<br />
        No external dependencies<br />
        Description page <a href="http://www.geoproc.com/be/bcSaveqml3.htm">here</a>.</p>
      </blockquote>
    </blockquote>
  </blockquote>
</blockquote>

<p><img src="http://www.geoproc.com/be/img/bcMultiStyles.png" width="48" height="48" align="absmiddle" />&nbsp;&nbsp;&nbsp;&nbsp;<strong>bcMultiStyles<sup>3</sup></strong>: Load/save multiple styles in qml's to/from a QGIS layer. The styles are saved as <a href="https://en.wikipedia.org/wiki/Sidecar_file" target="_blank">sidecars</a> in the same directory of the layer file, by default. Loading styles can be done from the sidecars or from a directory.</p>
<blockquote>
  <blockquote>
    <blockquote>
      <blockquote>
        <p>QGIS version 3.x (not compatible with versions &le; 2).<br />
        No external dependencies<br />
        Description page <a href="http://www.geoproc.com/be/bcMultiStyles3.htm">here</a>.</p>
      </blockquote>
    </blockquote>
  </blockquote>
</blockquote>

<p><img src="http://www.geoproc.com/be/img/bcStackP.png" width="48" height="48" align="absmiddle" />&nbsp;&nbsp;&nbsp;&nbsp;<strong>bcStackP<sup>3</sup></strong>: Create stacked profiles from point layers.</p>
<p>In geophysics, stacked profiles are commonly used to display geophysical data (magnetic, gravity, electromagnetic, electric, radiometric, ...) over the lines on which the data has been acquired. Correctly displayed they will show trends and anomalous areas that can be of interest.</p>
<blockquote>
  <blockquote>
    <blockquote>
      <blockquote>
        <p>QGIS version 3.x (not compatible with versions &le; 2).<br />
        External dependencies: numpy and pandas<br />
        Description page <a href="http://www.geoproc.com/be/bcStackP3.htm">here</a>.</p>
      </blockquote>
    </blockquote>
  </blockquote>
</blockquote>

<p><img src="http://www.geoproc.com/be/img/bcclr2tbl.png" width="48" height="48" align="absmiddle" />&nbsp;&nbsp;&nbsp;&nbsp;<strong>bcclr2tbl<sup>3</sup></strong>: Style a one-band raster layer using Golden Software Surfer colour ramp files (.clr).</p>
<blockquote>
  <blockquote>
    <blockquote>
      <blockquote>
        <p>QGIS version 3.x (not compatible with versions &le; 2).<br />
        No External dependencies<br />
        Description page <a href="http://www.geoproc.com/be/bcclr2tbl3.htm">here</a>.</p>
      </blockquote>
    </blockquote>
  </blockquote>
</blockquote>

<p><img src="http://www.geoproc.com/be/img/bcSwapYZ.png" width="48" height="48" align="absmiddle" />&nbsp;&nbsp;&nbsp;&nbsp;<strong>bcSwapYZ<sup>3</sup></strong>: Create a 3D vector by setting Z-coord to Y-coord and setting Y-coord to a constant.</p>
<p>This algo is for use in a 2D to 3D workflow, where QGIS raster georeferencer is used to digitalise a section (XZ) into an XY-raster, which is then digitalised (XY) and needs to be rotated to XZ-coords.</p>
<blockquote>
  <blockquote>
    <blockquote>
      <blockquote>
        <p>QGIS version 3.x (not compatible with versions &le; 2).<br />
        No External dependencies<br />
        Description page <a href="http://www.geoproc.com/be/bcSwapYZ3.htm">here</a>.</p>
      </blockquote>
    </blockquote>
  </blockquote>
</blockquote>

<p><img src="http://www.geoproc.com/be/img/bcGenRNDSurveyData.png" width="48" height="48" align="absmiddle" />&nbsp;&nbsp;&nbsp;&nbsp;<em>Just for fun!</em> - <strong>bcGenRNDSurveyData<sup>3</sup></strong>: Create dummy survey with line, tie-lines and noisy data.</p>
<p>Lines and tie lines are not straight lines. Noise is added to the X- &amp; Y-coords. Data is a periodic function with lots of noise and spikes.</p>
<blockquote>
  <blockquote>
    <blockquote>
      <blockquote>
        <p>QGIS version 3.x (not compatible with versions &le; 2).<br />
        External dependencies: numpy<br />
        Description page <a href="http://www.geoproc.com/be/bcGenRNDSurveyData3.htm">here</a>.</p>
      </blockquote>
    </blockquote>
  </blockquote>
</blockquote>

Download zip file [here](http://www.geoproc.com/be/geoprocAlgos.zip) for manual installation.

Add "http://www.geoproc.com/be/plugins.xml" to QGIS plugin repositories source for automatic installation. See HowTo [here](http://www.geoproc.com/be/repinst3.htm).

---

Last updated: 30 June 2019 - Version 3.12

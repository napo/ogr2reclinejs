ogr2reclinejs
-------------
if you use reclinejs and you want show geodata, you need a conversion in csv, and a field with a geojson geometry to display.
<br>This script reads the data from an OGR (ex. ESRI Shapefile) source and creates a cvs file with a field "GeoJSON" where stores a single geometry in geojson format.
<br>
In the case of point geometry type, the script generates a CSV file with the fields LAT and LON, otherwise creates a geojson string.

ATTENTION:
the script converts the coordinates in WGS84 (epsg:4326)

requirements
------------
GDAL binding for python<br>
http://pypi.python.org/pypi/GDAL/1.9.1

Example
-------
with an ESRI Shapefile with point geometry<br>
(the data in the example are open data with cc0 license)
<pre>
wget http://www.territorio.provincia.tn.it/geodati/712_Sedi_comunali_della_PAT__pup__12_12_2011.zip
unzip http://www.territorio.provincia.tn.it/geodati/712_Sedi_comunali_della_PAT__pup__12_12_2011.zip
python ogr2reclinejs.py <i>pupsedi07f</i>.shp
</pre>

Output file <i>pupsedi07f</i><strong>.cvs</strong>
(headers in first row)
<pre>
PERIMETER,COMU,AREA,LON,LAT
49767.3225177,39,67013655.1778,11.773502305996132,46.47643262636006
31015.9257141,46,25872033.6238,11.116940689711424,46.45539355182122
31148.5732236,36,25038741.4929,11.742433651377064,46.47694596119694
32414.1120528,88,30629279.1232,11.136952626670512,46.43908681182543
26279.9981388,27,19167373.4818,11.10820237197858,46.430823557150056
28158.6961106,113,23628453.2065,11.699810966529446,46.45683741870301
...
</pre>
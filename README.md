ogr2reclinejs
=============
if you use reclinejs and you want show geodata, you need a conversion in csv, and a field with a geojson geometry to display.
This script reads the data from an OGR source and creates a cvs file with a field "GeoJSON" where stores a single geometry in geojson format.

requirements
============
GDAL binding for python

http://pypi.python.org/pypi/GDAL/1.9.1

# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 21:22:51 2012
@author: Maurizio Napolitano
MIT License
"""
import os,csv

#search the right version of the
try:
    from osgeo import ogr,osr
except:
	import ogr,osr
from optparse import OptionParser

MAX_CSV_FIELD_SIZE = 131072

class OGR2Reclinejs():
	version = '1.0b'
	sr_wgs84 = None
	datasource = None
	outfiles = []
	geomtypes = []
	geojson = 'GeoJSON'
	X = 'LON'
	Y = 'LAT'
	formatfound = ''
	def __init__(self,infile,verbose=False):
		'''
				create a object with the source file (infile = geodata source)
				'''
		supportedformats = []
		self.sr_wgs84 = osr.SpatialReference()
		self.sr_wgs84.ImportFromEPSG(4326)

		driver = None
		for g in range(0,ogr.GetDriverCount()):
			supportedformats.append(ogr.GetDriver(g).GetName())
			driver= ogr.GetDriver(g)
			datasource = driver.Open(infile)
			if datasource != None:
				self.datasource = datasource
				self.formatfound = ogr.GetDriver(g).GetName()
				break

		if datasource is None:
			message = 'Could not find the driver for %s' % infile
			if verbose:
				message += "\n"
				message += "List of supported drivers:"
				for sf in supportedformats:
					message += "- %s\n" % sf
			raise Exception,message

		self.layers_fields = []
		for idx in range(0,datasource.GetLayerCount()):
			layer = datasource.GetLayer(idx)
			sr = layer.GetSpatialRef()
			if sr is None:
				raise Exception, 'Projection not present'
			fields = {}
			self.geomtypes.append(layer.GetGeomType())
			for s in layer.schema:
				print 'FOUND SCHEMA FIELD', s.GetName()
				fields[s.GetName().decode('latin-1')] = s.GetTypeName()
			self.layers_fields.append(fields)
			layer.ResetReading()

	def info(self):
		'''
				return a dictionary with some information about the source file
				format => the file format name
				num_layers => the numbers of layers present in the source (allowed by the GML and Tiger format)
				layer_* => the name of the layer number *
				'''
		data = {}
		if self.datasource != None:
			data['format'] = self.formatfound
			data["num_layer"] =  self.datasource.GetLayerCount()
			for i in range(0,self.datasource.GetLayerCount()):
				nl = "layer_" + i
				data[nl] = self.datasource.GetLayer(i).GetName()
		return data

	def metadata(self):
		'''return a list with the list of the type of fields'''
		layers_fields = []
		for i in range(0,len(self.layers_fields)):
			fields = self.layers_fields[i]
			if self.geomtypes[i] == 1:
				fields[self.X] = 'Geometry.X'
				fields[self.Y] = 'Geometry.Y'
			else:
				fields[self.geojson] = 'Geometry'
			layers_fields.append(fields)
		return layers_fields

	def outputfiles(self):
		'''return the list of the filenames for the conversion'''
		return self.outfiles

	def conversion(self,destdir=None):
		'''For each layer present in the source file create a csv file with the geometry field.
				If the geometry type is a point, use the fields LAT and LON, otherwise create a GeoJSON string
				'''
		try:
			for idx in range(0,self.datasource.GetLayerCount()):
				layer = self.datasource.GetLayer(idx)
				outfile = layer.GetName() + ".csv"
				if destdir is not None:
					outfile = destdir + os.sep + layer.GetName() + ".csv"
				self.outfiles.append(outfile)
				ofile = open(outfile, 'wb')
				writer = csv.writer(ofile, dialect='excel')
				head = []
				for f in self.layers_fields[idx]:
					field = f.decode('latin-1').encode('utf-8')
					print 'F:[%s]' % field
					head.append(field)
				if self.geomtypes[idx] == 1:
					head.append(self.X)
					head.append(self.Y)
				else:
					head.append(self.geojson)
				writer.writerow(head)
				sr_source = layer.GetSpatialRef()
				feature = layer.GetNextFeature()
				while feature:
					values = []
					for fname in self.layers_fields[idx]:
						v = feature.items().get(fname)
						#if v is None: print 'Missing value for fname', fname
						values.append( v.decode('latin-1').encode('utf-8') if type(v) == str else v )
					geometry = feature.GetGeometryRef()
					if (sr_source != self.sr_wgs84):
						ct = osr.CoordinateTransformation(sr_source, self.sr_wgs84)
						geometry.Transform(ct)
					if self.geomtypes[idx] == 1:
						x = geometry.GetPoint(0)[0]
						y = geometry.GetPoint(0)[1]
						values.append(x)
						values.append(y)
					else:
						geometry_json = geometry.ExportToJson().encode('utf-8')
						if len(geometry_json) <= MAX_CSV_FIELD_SIZE:
							values.append(geometry_json)
						else:
							print 'Skipping geometry line'
					writer.writerow(values)
					feature = layer.GetNextFeature()
				layer.ResetReading()
		except OSError as e:
			print e

def main():
	usage = "%prog [options] arg\n"
	usage += " version %s " % OGR2Reclinejs.version

	parser = OptionParser(usage)
	#FIXME parser.add_option("-o","--ouput",action="store",dest="output",help="output file\nif not specified is used the layer name with the csv extension")
	parser.add_option("-d", "--destinatiodir", action="store", dest="destdir", help="output directory - default is current directory, the name is the layer name with the .csv suffix",default=None)
	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="verbose output",default=False)
	parser.add_option("-I","--info",action="store_true",dest="info",help="show info file, you need to use also the -i parameter (tip: with the command ogrinfo you obtain more informations)",default=False)

	(options,args) = parser.parse_args()

	if len(args) == 0:
		parser.print_help()
	else:
		inputfile = args[0]
		v = False
		if options.verbose:
			v = True
		ogr2reclinejs = OGR2Reclinejs(inputfile,v)
		ogr2reclinejs.conversion(options.destdir)
		if v:
			idx = 0
			metadata = ogr2reclinejs.metadata()
			for f in ogr2reclinejs.outputfiles():
				print "file %s" % f
				print "\tfields for %s:" % f
				mt = metadata[idx]
				for m in mt:
					print "\t\t%s => %s" % (m,mt[m])
				idx += 1

if __name__ == "__main__":
	main()
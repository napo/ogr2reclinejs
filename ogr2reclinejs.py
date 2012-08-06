# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 21:22:51 2012
@author: Maurizio Napolitano
MIT License
"""
import os,csv
try:
    from osgeo import ogr,osr
except:
    import ogr,osr
from optparse import OptionParser

class OGR2Reclinejs():
    sr_wgs84 = None
    datasource = None
    outfiles = []
    layers_fields = []
    geojson = 'GeoJSON'
    formatfound = ''
    def __init__(self,infile,verbose=False): 
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
            
        for idx in range(0,datasource.GetLayerCount()):
            layer = datasource.GetLayer(idx)
            sr = layer.GetSpatialRef() 
            if sr is None:
                raise Exception, 'Projection not present'
            fields = {}
            for s in layer.schema:
                fields[s.GetName()] = s.GetTypeName()
            self.layers_fields.append(fields)
            layer.ResetReading()
            
    def info(self):
        data = {}
        if self.datasource != None:
            data['format'] = self.formatfound
            data["num_layer"] =  self.datasource.GetLayerCount()
            for i in range(0,self.datasource.GetLayerCount()):
                nl = "layer_" + i
                data[nl] = self.datasource.GetLayer(i).GetName()
        return data
        
    def metadata(self):
        layers_fields = []
        for i in range(0,len(self.layers_fields)):
            fields = self.layers_fields[i]
            fields[self.geojson] = 'Geometry'
            layers_fields[i] = fields
        return layers_fields
        
    def outputfiles(self):
        return self.outfiles

    def conversion(self,destdir=None):
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
                    head.append(f)
                head.append(self.geojson)
                writer.writerow(head)
                sr_source = layer.GetSpatialRef() 
                feature = layer.GetNextFeature()
                while feature:
                    values = []
                    for i in range(0,len(self.layers_fields[idx])):
                        values.append(feature.GetField(i))
                    geometry = feature.GetGeometryRef()
                    ct = osr.CoordinateTransformation(sr_source, self.sr_wgs84)
                    geometry.Transform(ct)
                    values.append(geometry.ExportToJson())
                    writer.writerow(values)
                    feature = layer.GetNextFeature()
                layer.ResetReading()
        except OSError as e:
            print e

def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)  
    parser.add_option("-i", "--input", action="store", dest="input", help="input file")
    parser.add_option("-o","--ouput",action="store",dest="output",help="output file\nif not specified is used the layer name with the csv extension")
    parser.add_option("-f", "--filetype", action="store", dest="filetype", help="input file type - default is ESRI Shapefile",default='ESRI Shapefile')
    parser.add_option("-d", "--destinatiodir", action="store", dest="destdir", help="output directory - default is current directory",default=None)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="verbose output",default=False)
    parser.add_option("-I","--info",action="store",dest="info",help="show info file (tips: use the ogrinfo)",default=False)
    (options,args) = parser.parse_args()
    if options.input is None:
        parser.print_help()
    else:
        v = False
        if options.verbose:
            v = True
        ogr2reclinejs = OGR2Reclinejs(options.input,v)
        ogr2reclinejs.conversion(options.destdir)
        if v:
            idx = 0
            metadata = ogr2reclinejs.metadata()
            for f in ogr2reclinejs.outputfiles():
                print "File %s created:" % f
                print "\tFields for %s:" % f
                mt = metadata[idx]
                for m in metadata:
                    print "\tfield\ttype"
                    print "\t%s\t%s" % (m,mt[m])
                idx += 1

if __name__ == "__main__":
    main()

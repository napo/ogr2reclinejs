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
    fields = {}
    geojson = 'geojson'
    
    def __init__(self,infile,filetype='ESRI Shapefile'): 
        self.sr_wgs84 = osr.SpatialReference()
        self.sr_wgs84.ImportFromEPSG(4326)
        self.filetype=filetype
        driver = ogr.GetDriverByName(self.filetype)
        self.datasource = driver.Open(infile)
        if self.datasource is None:
            message = 'Could not open ' + infile
            message += "\n"
            message += "Supported formats:\n"
            for g in range(0,ogr.GetDriverCount()):
                message += ogr.GetDriver(g).GetName() + "\n"
            raise Exception, message
        for idx in range(0,self.datasource.GetLayerCount()):
            layer = self.datasource.GetLayer(idx)
            sr = layer.GetSpatialRef() 
            if sr is None:
                raise Exception, 'Projection not present'
            self.fields = {}
            for s in layer.schema:
                self.fields[s.GetName()] = s.GetTypeName()
            layer.ResetReading()

    def metadata(self):
        mfields = self.fields
        mfields['geometry'] = self.geojson
        return mfields
        
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
                for f in self.fields:
                    head.append(f)
                head.append(self.geojson)
                writer.writerow(head)
                sr_source = layer.GetSpatialRef() 
                feature = layer.GetNextFeature()
                while feature:
                    values = []
                    for i in range(0,len(self.fields)):
                        values.append(feature.GetField(i))
                    geometry = feature.GetGeometryRef()
                    ct = osr.CoordinateTransformation(sr_source, self.sr_wgs84)
                    geometry.Transform(ct)
                    values.append(geometry.ExportToJson())
                    writer.writerow(values)
                    feature = layer.GetNextFeature()
                layer.ResetReading()
        except EOFError as e:
            print e

def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)  
    parser.add_option("-i", "--input", action="store", dest="input", help="input file")
    parser.add_option("-f", "--filetype", action="store", dest="filetype", help="input file type - default is ESRI Shapefile",default='ESRI Shapefile')
    parser.add_option("-d", "--destinatiodir", action="store", dest="destdir", help="output directory - default is same directory of input file",default=None)
    (options,args) = parser.parse_args()
    if options.input is None:
        parser.print_help()
    else:
        ogr2reclinejs = OGR2Reclinejs(options.input,options.filetype)
        ogr2reclinejs.conversion(options.destdir)
        ff = ogr2reclinejs.outputfiles()
        m = "file"
        if len(ff) > 1:
            m = "%i files" % (len(ff))
        m += "generated\n"
        for f in ff:
            m += "-%s\n" % (f)
        print m
        print "\n"
        print "Fields: name and type"
        metadata = ogr2reclinejs.metadata()
        for m in metadata:
            print "%s => %s" % (m,metadata[m])
        print "----"
        print "File %s generated" % f
if __name__ == "__main__":
    main()

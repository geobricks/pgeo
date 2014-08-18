from pgeo.gis.gdal_calc import calc_layers



#files_path = "/home/vortex/Desktop/LAYERS/TRMM/04/*.tif"
#files_path = ["/home/vortex/Desktop/LAYERS/TRMM/Rainfall_06_2014.tif", "/home/vortex/Desktop/LAYERS/TRMM/Rainfall_05_2014.tif"]
#outputfile = "/home/vortex/Desktop/result_last_sum2.tif"

# print "Created (%s) layer %s" % (calc_layers(files_path, outputfile, "avg"), outputfile)
# print "Created (%s) layer %s" % (calc_layers(files_path, outputfile, "sum"), outputfile)
#print "Created (%s) layer %s" % (gdal_calc.calc_layers(files_path, outputfile, "sum"), outputfile)
# print "Created (%s) layer %s" % (calc_layers(files_path, outputfile, "diff"), outputfile)

# files_path = ["/home/vortex/Desktop/LAYERS/TRMM/04/*.tif"]
# outputfile = "/home/vortex/Desktop/result_last_sum.tif"
#
# print "Created (%s) layer %s" % (calc_layers(files_path, outputfile, "avg"), outputfile)


def calc_trmm(year, month):
    try:
        files_path = "/home/vortex/Desktop/LAYERS/TRMM/" + year+ "/" + month + "/*.tif"
        print files_path
        outputfile = "/home/vortex/Desktop/LAYERS/TRMM/" + year+ "/" + month + "/trmm_"+ month +"_"+ year +".tif"
        print outputfile
        calc_layers(files_path, outputfile, "sum")
    except Exception, e:
        print e
        pass

# Parameters
years = ['2012', '2013', '2014']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
product = '3B42RT'

for year in years:
    for month in months:
        calc_trmm(year, month)





from pgeo.gis import gdal_calc

#files_path = "/home/vortex/Desktop/LAYERS/TRMM/04/*.tif"
files_path = ["/home/vortex/Desktop/LAYERS/TRMM/Rainfall_06_2014.tif", "/home/vortex/Desktop/LAYERS/TRMM/Rainfall_05_2014.tif"]
outputfile = "/home/vortex/Desktop/result_last_sum2.tif"

# print "Created (%s) layer %s" % (calc_layers(files_path, outputfile, "avg"), outputfile)
# print "Created (%s) layer %s" % (calc_layers(files_path, outputfile, "sum"), outputfile)
print "Created (%s) layer %s" % (gdal_calc.calc_layers(files_path, outputfile, "sum"), outputfile)
# print "Created (%s) layer %s" % (calc_layers(files_path, outputfile, "diff"), outputfile)

# files_path = ["/home/vortex/Desktop/LAYERS/TRMM/04/*.tif"]
# outputfile = "/home/vortex/Desktop/result_last_sum.tif"
#
# print "Created (%s) layer %s" % (calc_layers(files_path, outputfile, "avg"), outputfile)
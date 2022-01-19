# import laspy.file
# import laspy.header

import rasterio as rio
from rasterio.warp import transform
from rasterio.crs import CRS
import subprocess
import json
import sys
import logging


LOG_FORMAT = '[%(levelname)s] %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=LOG_FORMAT)



def pc2dtm(file_path, grid_size, horizontal_srs_wkt, WORKING_DIR):

	# get the crs from the las file
	# the same crs will be used for the output raster
	# crs_las = {'init': 'EPSG:3945'}
	crs_las = CRS.from_string(horizontal_srs_wkt)

	pipeline_min = [
		file_path,
		{
			"type":"writers.gdal",
			"filename":str(WORKING_DIR/"min.tif"),
			"output_type":"min",
			"gdaldriver":"GTiff",
			"window_size":3,
			"resolution":grid_size
		}
	]

	with open(WORKING_DIR / 'pipeline_min.json', 'w') as outfile:
		json.dump(pipeline_min, outfile)

	logging.debug('Generating min rasters...')
	#generate rasters: min (description of pipelines in .json files)
	subprocess.run('pdal pipeline '+str(WORKING_DIR/'pipeline_min.json'), shell=True)


	logging.debug('adding a crs to the raster...')

	dataset_min = rio.open(WORKING_DIR/'min.tif')

	new_dataset = rio.open(WORKING_DIR/'output.tif', 'w',
									driver = dataset_min.driver,
									nodata = dataset_min.nodata,
									height=dataset_min.height, width=dataset_min.width,
									count=dataset_min.count, dtype=rio.float64,
									crs=crs_las, transform=dataset_min.transform)

	band_min = dataset_min.read(1)

	new_dataset.write(band_min, 1)

	logging.debug('All done')


# if __name__ == "__main__":

# 	pc2dtm('input.las', 0.2)
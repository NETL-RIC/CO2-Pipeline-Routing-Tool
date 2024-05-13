"""
These is Lucy's script for converting coordinates.
This is not imported as a module anywhere, nor is it ran.
It's just here for reference, for now.
"""

from osgeo import gdal, ogr, osr

def IndicesToCoordinates(raster_wgs84, indices):
    """
    Converts indexed raster locations into spatial coordinates.

    Parameters:
        raster_wgs84 - path to raster location
        index - tuple of x,y indices

    returns:
        (longitude, latitude) in same spatial reference system as input raster
    """

    ds = gdal.Open(raster_wgs84)

    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()

    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())

    x = indices[0] * x_size + upper_left_x + (x_size / 2)  # add half the cell size
    y = indices[1] * y_size + upper_left_y + (y_size / 2)  # to centre the point

    return(x,y)


def CoordinatesToIndices(raster_wgs84, coordinates):
    """
    Converts spatial coordinates to indexed raster locations

    Parameters:
        raster_wgs84 - path to raster location
        coordinates - tuple of longitude, latitude

    returns:
        (x, y) as indexed locations
    """

    ds = gdal.Open(raster_wgs84)

    # Reverse ---> coordinates to indices #TODO: implement when passing the coordinates to the ML
    geotransform = ds.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]

    xOffset = int((coordinates[0] - originX)/pixelWidth)
    yOffset = int((coordinates[1] - originY)/pixelHeight)

    return((xOffset, yOffset))


raster_file = r"C:\Users\romeolf\Desktop\ras_10km_01252024_WGS84.tif" #Original raster in WGS84
index_list = [(0,0),(54,68),(400,200), (450, 250)]


for indice_tuple in index_list:

    coordinate_tuple = IndicesToCoordinates(raster_file, indice_tuple)

    indice_tuple_check = CoordinatesToIndices(raster_file, coordinate_tuple)

    print(f"{indice_tuple} -> {coordinate_tuple} -> {indice_tuple_check}")
    print(f"{indice_tuple} SHOULD MATCH {indice_tuple_check}")


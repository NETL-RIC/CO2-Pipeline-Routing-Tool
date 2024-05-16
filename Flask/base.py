import os.path
import sys

from flask import Flask, request
import fiona
import torch
from osgeo import gdal, ogr, osr
import numpy as np

from controller import PipelineController
from line_builder import line_builder

api = Flask(__name__)

@api.route('/profile')
def my_profile():
    response_body = {
        "name": "CO2 Pipeline Routing App",
        "about": "Web app to generate CO2 Pipelines across the USA and Alaska"
    }

    return response_body


@api.route('/token', methods=['GET', 'POST'])
def a():
    """ API endpoint for generating route based on user-specified points

    Parameters: none, but provides 
    Returns: route: line, the generated line in wgs84 to be plotted in the browser
    """

    if request.method == 'POST':
        shparray = []

        start = request.json.get("s", None)
        end = request.json.get("e", None)
        print(f'Got start: {start} and end: {end} from frontend')

        print("Generating line...")
        route = generate_line_ml(start, end)    # using dummy values until translation is fixed

        print("Sending route to frontend...")
        line_builder(route)
        return route

def generate_line_ml(start, dest):
    """ Call machine learning functions to generate line between parameter points

    Paramters: start, dest: tuple, the start and end points of the line that will be generated, passed in as WGS84 coords
    Returns: route: list, the list of coordinates that composes the line
    """

    raspath = './raster/ras_10km_resampled_071323_WGS84.tif'
    print("Original wgs84 start: " + str(start))
    print("Original wgs84 dest: " + str(dest))
    print("\n")

    startlocal = CoordinatesToIndices(raspath, start)   # translate WGS84 coords into local raster index coords for ML processing
    destlocal = CoordinatesToIndices(raspath, dest)

    print("Translated start into local coords (as x,y): " + str(startlocal))
    print("Translated dest into local coords (as x,y):" + str(destlocal))
    print("\n")

    pipecontrol = PipelineController(startlocal, destlocal)
    route_local = pipecontrol.ml_run()
    print("\n")
    print("Length of list:" + str(len(route_local)))

    print("First point in list of points, as Lucy Local System:" + str(route_local[0]))
    print("Last point in list of points, as Lucy Local System:" + str(route_local[-1]))
    print("\n")

    route_wgs = translateLine(raspath, route_local)
    print("First point from list of points, translated back to wgs84: " + str(route_wgs[0]))
    print("Last point from list of points, translated back to wgs84: " + str(route_wgs[-1]))
    print("\n")


    # Using dummy values until translation is accurate
    return route_wgs

def generate_dummy_line(start=(37.779259, -122.419329), dest=(39.739236, -104.990251)):
    """ Generates a line object via interpolation between two supplied WGS points for testing purposes
    Default vals are SFO and Denver in WGS84, respectively, by default.
    
    Paramters: start, dest: tuple, start and end point of the line to generate
    Return: interpline: list, the generated line between the two supplied points as a list of coordinates
    """
    listlen = 501 # the ML code seems to always return a list of length 501
    linerange_x = abs(start[0] - dest[0])
    linerange_y = abs(start[1] - dest[1])
    
    step_x = linerange_x / listlen
    step_y = linerange_y / listlen

    dummyline = []

    for i in range(listlen):
        x = start[0] + (i * step_x)
        y = start[1] + (i * step_y)
        # y = np.interp(x, start, dest)
        dummyline.append((x,y))

    print("Using dummy line from SFO to Denver")
    return dummyline

def translateLine(raster_wgs84, routelist):
    """ Translates provided line from local ml coord (raster indices) system to WGS84.
    Modified from IndicesToCoords.
    Destructively changes routelist in place.

    Paramters: 
        raster_wgs84: string, relative or abs path to raster location
        routelist: list, collection of points that form a line

    Returns:
        wgsList: list, original coordinate list translated from local coords to wgs84
    """

    ds = gdal.Open(raster_wgs84)

    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()

    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())

    for i, coord in enumerate(routelist):
        coord = (coord[-1], coord[0])
        x = coord[0] * x_size + upper_left_x + (x_size / 2)  # add half the cell size
        y = coord[1] * y_size + upper_left_y + (y_size / 2)  # to centre the point
        routelist[i] = (y,x)

    return routelist

def CoordinatesToIndices(raster_wgs84, coordinates):
    """
    Converts spatial coordinates to indexed raster locations

    Parameters:
        raster_wgs84 - path to raster location
        coordinates - tuple of longitude, latitude

    returns:
        (x, y) as indexed locations
    """

    coordinates = (coordinates[-1], coordinates[0])

    ds = gdal.Open(raster_wgs84)

    # Reverse ---> coordinates to indices #TODO: implement when passing the coordinates to the ML
    geotransform = ds.GetGeoTransform()
    """
    print("--------------------------")
    print(geotransform)
    print("--------------------------")
    """
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]

    xOffset = int((coordinates[0] - originX)/pixelWidth)
    yOffset = int((coordinates[1] - originY)/pixelHeight)

    return((yOffset, xOffset))

def IndicesToCoordinates(raster_wgs84, indices):
    """
    Converts indexed raster locations into spatial coordinates.

    Parameters:
        raster_wgs84 - path to raster location
        index - tuple of x,y indices

    returns:
        (longitude, latitude) in same spatial reference system as input raster
    """

    # indices = (indices[-1], indices[0])

    ds = gdal.Open(raster_wgs84)

    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()

    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())

    x = indices[0] * x_size + upper_left_x + (x_size / 2)  # add half the cell size
    y = indices[1] * y_size + upper_left_y + (y_size / 2)  # to centre the point

    # note: this is actually returning in (x, y)
    return(y,x)


def test_ml():
    """ Dummy function to test point translation and ml function without needing to interact with frontend
    """
    raspath = './raster/ras_10km_resampled_071323_WGS84.tif'

    startwgs = (35.23, -101.71) # amarillo, tx
    destwgs =(31.9973, -102.0779) # midland, tx

    print("Original wgs84 start: " + str(startwgs))
    print("Original wgs84 dest: " + str(destwgs))
    print("\n")

    startlocal = CoordinatesToIndices(raspath, startwgs)
    destlocal = CoordinatesToIndices(raspath, destwgs)

    # Some coords supplied by ben to test funcitonality
    startlocal2 = (274, 390)
    destlocal2 = (248, 364)
    startlocal3 = (256, 557)
    destlocal3 = (268, 579)
    startlocal4 = (242, 476)
    destlocal4 = (261, 476)

    print("Translated start into local coords (as x,y): " + str(startlocal))
    print("Translated dest into local coords (as x,y):" + str(destlocal))
    print("\n")

    pipecontrol = PipelineController(startlocal, destlocal)

    # this is in Y, X
    route_local = pipecontrol.ml_run() #list of all points that compose the line route
    print("\n")
    print("Length of list:" + str(len(route_local)))

    print("First point in list of points, as Lucy Local System:" + str(route_local[0]))
    print("Last point in list of points, as Lucy Local System:" + str(route_local[-1]))
    print("\n")

    # translate back to wgs84 to give back to front-end
    # this is in X, Y
    route_wgs = translateLine(raspath, route_local)
    print("First point from list of points, translated back to wgs84: " + str(route_wgs[0]))
    print("Last point from list of points, translated back to wgs84: " + str(route_wgs[-1]))
    print("\n")

test_ml()


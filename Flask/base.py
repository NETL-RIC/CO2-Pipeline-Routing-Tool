import os.path
import os
import sys
from pathlib import Path

import shutil
import glob
from flask import Flask, request
import fiona
import torch
from osgeo import gdal, ogr, osr
import numpy as np

from controller import PipelineController
from line_builder import line_builder
from report_builder.report_builder import report_builder

api = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'user_uploads')

@api.route('/profile')
def my_profile():
    response_body = {
        "name": "CO2 Pipeline Routing App",
        "about": "Web app to generate CO2 Pipelines across the USA and Alaska"
    }

    return response_body

@api.route('/uploads', methods = ['POST'])
def uploads_file():
    print('hello')
    delete_dir_contents('user_uploads')     #clear out stuff from a previous tool run
    name = ''
    file = request.files
    print(file)
    for i in file:
        name = file[i].filename
        print(name)
        # file[i].save(os.path.join(UPLOAD_FOLDER, name))
        cur_dir = os.path.dirname(__file__)
        file_path = os.path.join('./user_uploads', name)
        file[i].save(file_path)
    
    ret = []
    c = fiona.open(file_path)
    shptype = c.schema["geometry"]
    print('The uploaded shapefile is of type:')
    print('\t'+shptype)
    
    with fiona.open(file_path) as lines:
        for line in lines:
            v = line['geometry']['coordinates']

            if type(v[0]) == list:
                new_list = [(y, x)  for x, y in v[0]]
            else:
                new_list = [(y, x)  for x, y in v]

            ret.append(new_list)
    
    v = {
        'array': ret,
        'typ': shptype
    }
    print('The uploaded shapefile is of type:')
    print('\t'+shptype)

    if shptype == "LineString":
        print("Creating PDF report for LineString shapefile")
        run_line_eval_mode(v['array'][0], v['array'][-1])
    elif shptype == "Polygon":
        print("Creating PDF report for Polygon shapefile")
        run_line_eval_mode(v['array'][0], v['array'][-1])
    else:
        print("Uploaded shapefile is neither a polygon or a line. Please upload an appropriate shapefile.")
    
    return v

def run_line_eval_mode(first_point, last_point):
    """ Create eval report from user-uploaded LINE shapefiles on button click
    Connected to 'Perform Analysis' in the evaluation mode section of the webpage
    Params: shp_type(string): if the user's shapefile is a line or polygon
    Returns: none
    """
    shp_extension_file = None
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "user_uploads")):
        if file.endswith(".shp"):
            shp_extension_file = file
            print(f"Found user-uploaded file: {shp_extension_file}")

    if shp_extension_file == None:
        print('No .shp file found in user_uploads')
    else:
        output_shp_abspath = os.path.join(os.path.dirname(__file__), "user_uploads", shp_extension_file)
        delete_prev_zips_pdfs()
        public_abspath = os.path.realpath('../public')
        pdfname = report_builder(output_shp_abspath, first_point, last_point, public_abspath)    # create pdf report in '../public' so front-end can grab it easily
        os.rename(os.path.join(public_abspath, pdfname), os.path.join(public_abspath, "route_report.pdf"))


def delete_dir_contents(rel_path):
    """ Delete everything in provided folder name that exists in Flask. Ie 'output_shapefiles'
    This keeps the directories clean, and allows us to make a zip file by just passing in a directory name.
    Params: rel_path: a path relative to Flask/
    Returns: none
    """
    if (len(os.listdir((rel_path)))) == 0:
        print(f"Directory {rel_path} is already empty, no need to delete.")
    else:
        print('\tdelete_dir_contants called, deleting contents of '+rel_path+'...')
        rel_path = os.path.abspath(rel_path)
        rel_path  = rel_path +'/*'
        files = glob.glob(rel_path)
        count = 0
        for f in files:
            os.remove(f)
            count = count + 1
        print(f'\tdeleted all {count} contents of {rel_path}.')

def delete_prev_zips_pdfs():
    """ Delete *.zip from ../public
    params: none
    returns: none
    """
    #dirname = os.path.abspath('../public')
    dircontents = os.listdir('../public')

    for file in dircontents:
        if file.endswith(".zip") or file.endswith(".pdf"):
            print(f"\t delete_prev_zips: deleting old file {file}")
            os.remove(os.path.join('../public', file))

def create_output_zip(zipname):
    """ Creates .zip based on contents of output_shapefiles in the proj root dir's /public folder
    params: zipname: string, the name of the zip to be created
    """
    zipname = 'route_shapefile_and_report'    # TEMPORARY SOLUTION, eventually pass the name to frontend to download
    dest_path = os.path.join(os.path.realpath('../public'), zipname)
    shutil.make_archive(dest_path, 'zip', 'output')
    print("\tcreate_output_shp_zip: created zipfile at ../public")




@api.route('/token', methods=['GET', 'POST'])
def a():
    """ API endpoint for generating route based on user-specified points. Makes report and sends to .zip in /public in the root project dir.
    Parameters: none
    Returns: route: line, the generated line in wgs84 to be plotted in the browser
    """

    if request.method == 'POST':

        start = request.json.get("s", None)
        end = request.json.get("e", None)

        route = generate_line_ml(start, end)    # calculate line with ML

        first_point = route[0]
        last_point = route[-1]  
        print(f"After ML, start point is {first_point}")
        print(f"After ML, dest: point is {last_point}")

        delete_dir_contents('output')   # delete the shapefiles/pdfs from the last tool run

        shpinfo = line_builder(route)  # create shapefile(s) in ./output, based on line, return filename of output .shp file
        output_shp_abspath = shpinfo[1]
        output_shp_filename = shpinfo[0]
       
        pdf_name = report_builder(output_shp_abspath, first_point, last_point, "output")    # create pdf report in './output
        delete_prev_zips_pdfs()                   # delete zip from last run if exist
        create_output_zip(output_shp_filename) # create zip of pdf/shp files in ../public so front-end can easily grab
        return route

def generate_line_ml(start, dest):
    """ Call machine learning functions to generate line between parameter points

    Paramters: start, dest: tuple, the start and end points of the line that will be generated, passed in as WGS84 coords
    Returns: route: list, the list of coordinates that composes the line
    """

    raspath = './raster/ras_10km_resampled_071323_WGS84.tif'    # old raster
    # raspath = './cost_surfaces/raw_cost_10km_aea/cost_10km_aea.tif' # new raster for new ml. needs translation functions from Lucy
    print("/Flask/base.generate_line_ml:")
    print("\tOriginal wgs84 start: " + str(start))
    print("\tOriginal wgs84 dest: " + str(dest))
    print("\n")

    startlocal = CoordinatesToIndices(raspath, start)   # translate WGS84 coords into local raster index coords for ML processing
    destlocal = CoordinatesToIndices(raspath, dest)
    print("Start Coord passed to ML:" + str(startlocal))
    print("Dest Coord passed to ML:" + str(destlocal))

    pipecontrol = PipelineController(startlocal, destlocal)
    route_local = pipecontrol.ml_run()

    print("First point in list of points, as Lucy Local System:" + str(route_local[0]))
    print("Last point in list of points, as Lucy Local System:" + str(route_local[-1]))

    # write post-ml route list to a file for Ben to troubleshoot... remove later
    with open('post-ml-line.txt','w') as f:
        for line in route_local:
            f.write(f"{line}\n")

    route_wgs = translateLine(raspath, route_local)
    print("\troute_wgs[0]: " + str(route_wgs[0]))
    print("\troute_wgs[1]: " + str(route_wgs[-1]))
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

    geotransform = ds.GetGeoTransform()

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

#test_ml()


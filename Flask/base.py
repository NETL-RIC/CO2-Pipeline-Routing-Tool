import os.path
import os
import sys
import webbrowser
from pathlib import Path

import shutil
import glob
from flask import Flask, request, render_template
import fiona
import torch
from osgeo import gdal, ogr, osr
import numpy as np

from controller import PipelineController
from line_builder import line_builder
from report_builder.report_builder import report_builder
from extra_utils import resource_path

api = Flask(__name__, static_url_path='', static_folder='build', template_folder='build')
# APP_ROOT = os.path.dirname(os.path.realpath(__file__))

if getattr(sys, 'frozen', False):
    APP_ROOT = os.path.dirname(sys.executable)
elif __file__:
    APP_ROOT = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'user_uploads')

@api.route('/')
def index():
    return render_template('index.html')

@api.route('/profile')
def my_profile():
    response_body = {
        "name": "CO2 Pipeline Routing App",
        "about": "Web app to generate CO2 Pipelines across the USA and Alaska"
    }

    return response_body

@api.route('/help', methods = ['POST'])
def open_help():
    h_path = resource_path("documentation/_build/html/index.html")
    print(os.path.exists(h_path))
    webbrowser.open(f"file://{h_path}")
    return(h_path)

# Evaluate button 
@api.route('/uploads', methods = ['POST'])
def uploads_file():
    print('hello')
    try:
        delete_dir_contents(resource_path('user_uploads'))     #clear out stuff from a previous tool run
    except PermissionError as e:
        print("Got permission error from locked file:", e)
    name = ''
    file = request.files
    print(file)
    for i in file:
        print(i)
        name = file[i].filename
        print(name)
        # file[i].save(os.path.join(UPLOAD_FOLDER, name))
        # cur_dir = os.path.dirname(__file__)
        file_path = os.path.join(resource_path('user_uploads'), name)
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


    pdf_path = None
    if shptype == "LineString":
        print("Creating PDF report for LineString shapefile")
        # first_point = v['array'][0] # unnessecary right now, but in case it's needed later
        # last_point = v['array'][-1] # unnessecary right now, but in case it's needed later
        pdf_path = run_line_eval_mode()
    elif shptype == "Polygon":
        print("Creating PDF report for Polygon shapefile")
        pdf_path = run_line_eval_mode()
    else:
        print("Uploaded shapefile is neither a polygon or a line. Please upload an appropriate shapefile.")
    
    v['pdf'] = pdf_path

    return v

# Evaluate button
def run_line_eval_mode():
    """ Create eval report from user-uploaded LINE shapefiles on button click
    Connected to 'Perform Analysis' in the evaluation mode section of the webpage
    Params: shp_type(string): if the user's shapefile is a line or polygon
    Returns: none
    """
    shp_extension_file = None
    for file in os.listdir(resource_path("user_uploads")):
        if file.endswith(".shp"):
            shp_extension_file = file
            print(f"Found user-uploaded file: {shp_extension_file}")

    if shp_extension_file == None:
        print('No .shp file found in user_uploads')

        return None
    else:
        output_shp_abspath = os.path.join(resource_path("user_uploads"), shp_extension_file)
        delete_prev_zips_pdfs()
        public_abspath = resource_path('public')
        if not os.path.exists(public_abspath):
            os.mkdir(public_abspath)
            print(f"Created public folder at {public_abspath}")
        pdfname = report_builder(shapefile=output_shp_abspath, out_path=public_abspath)    # create pdf report in '../public' so front-end can grab it easily
        print("Created pdf report")
        new_pdf_path = os.path.join(public_abspath, "route_report.pdf")
        os.rename(os.path.join(public_abspath, pdfname), new_pdf_path)
        
        return new_pdf_path


def delete_dir_contents(rel_path):
    """ Delete everything in provided folder name that exists in Flask. Ie 'output_shapefiles'
    This keeps the directories clean, and allows us to make a zip file by just passing in a directory name.
    Params: rel_path: a path relative to Flask/
    Returns: none
    """
    if not os.path.exists(rel_path):
        os.mkdir(rel_path)
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
    public_path = resource_path('public')
    if os.path.exists(public_path):
        dircontents = os.listdir(public_path)

        for file in dircontents:
            if file.endswith(".zip") or file.endswith(".pdf"):
                print(f"\t delete_prev_zips: deleting old file {file}")
                os.remove(os.path.join(public_path, file))
    else:
        print(f'There was no public folder {public_path} to delete zips from')

def create_output_zip(zipname):
    """ Creates .zip based on contents of output_shapefiles in the proj root dir's /public folder
    params: zipname: string, the name of the zip to be created
    """
    zipname = 'route_shapefile_and_report'    
    # dest_path = os.path.join(os.path.realpath('public'), zipname)
    public_f = resource_path('public')
    dest_path = os.path.join(public_f, zipname)
    if not os.path.exists(public_f):
        os.mkdir(public_f)
    shutil.make_archive(dest_path, 'zip', resource_path('output'))
    print(f"\tcreate_output_shp_zip: created zipfile at f{dest_path}")
    return dest_path + '.zip'


@api.route('/token', methods=['GET', 'POST'])
def a():
    """ API endpoint for generating route based on user-specified points. Makes report and sends to .zip in /public in the root project dir.
    Parameters: none
    Returns: route: line, the generated line in wgs84 to be plotted in the browser
    """

    if request.method == 'POST':
        print("Generate Pipeline request recieved")

        start = request.json.get("s", None)
        end = request.json.get("e", None)
        print(f"From frontend, start is: {start}")
        print(f"From frontend, end is: {end}")

        route = generate_line_ml(start, end)    # calculate line with ML

        first_point = route[0]
        last_point = route[-1]  
        print(f"After ML, start point is {first_point}")
        print(f"After ML, dest: point is {last_point}")

        delete_dir_contents(resource_path('output'))   # delete the shapefiles/pdfs from the last tool run

        shpinfo = line_builder(route)  # create shapefile(s) in ./output, based on line, return filename of output .shp file
        output_shp_abspath = shpinfo[1]
        output_shp_filename = shpinfo[0]
       
        pdf_name = report_builder(output_shp_abspath, first_point, last_point, "output")    # create pdf report in './output
        # delete_prev_zips_pdfs()                   # delete zip from last run if exist
        zip_path = create_output_zip(output_shp_filename) # create zip of pdf/shp files in ../public so front-end can easily grab
        route_correct_swap = []
        for coord in route:
            route_correct_swap.append((coord[1], coord[0]))
            
        print(f"First and last coord, about to go to frontend {route[0]}, {route[-1]}")
        return {'route': route_correct_swap, 'zip':zip_path}

def generate_line_ml_old(start, dest):
    """ Call machine learning functions to generate line between parameter points

    Paramters: start, dest: tuple, the start and end points of the line that will be generated, passed in as WGS84 coords
    Returns: route: list, the list of coordinates that composes the line
    """

    raspath = resource_path('raster/ras_10km_resampled_071323_WGS84.tif')    # old raster
    # raspath = './cost_surfaces/raw_cost_10km_aea/cost_10km_aea.tif' # new raster for new ml. needs translation functions

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

def translateLine_old(raster_wgs84, routelist):
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

def CoordinatesToIndices_old(raster_wgs84, coordinates):
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

def IndicesToCoordinates_old(raster_wgs84, indices):
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



#Slightly modified
def CoordinatesToIndices(raster, coordinates):
    """
    Converts spatial coordinates to indexed raster locations
    Parameters:
        raster - path to raster location
        coordinates - tuple of longitude, latitude
    returns:
        (x, y) as indexed locations
    """

    coordinates = (coordinates[-1], coordinates[0])
    # Convert coordinates from WGS 84 to Albers Equal Area to work with raster
    aea_coordinates = Wgs84ToAea(coordinates) #Stephen, added this line here so function works same


    ds = gdal.Open(raster)
    geotransform = ds.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    xOffset = int((aea_coordinates[0] - originX) / pixelWidth)
    yOffset = int((aea_coordinates[1] - originY) / pixelHeight)
    ds = None
    return ((yOffset, xOffset))


#Slightly modified
def IndicesToCoordinates(raster, indices):
    """
    Converts indexed raster locations into spatial coordinates.
    Parameters:
        raster - path to raster location
        index - tuple of x,y indices
    returns:
        (longitude, latitude) in same spatial reference system as input raster
    """
    # indices = (indices[-1], indices[0])
    ds = gdal.Open(raster)
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    x = indices[0] * x_size + upper_left_x + (x_size / 2)  # add half the cell size
    y = indices[1] * y_size + upper_left_y + (y_size / 2)  # to centre the point
    # note: this is actually returning in (x, y)

    # Convert from Albers Equal Area into longitude, latitude in WGS 84
    wgs84_coordinates = AeaToWgs84((x, y)) #Stephen, I added this and the next line so the function operates the same
                                            # as before and returns latitude, longitude in WGS84
    (y, x) = wgs84_coordinates[1], wgs84_coordinates[0]
    ds = None
    return (y, x)


#Slightly modified
def translateLine(raster, routelist):
    """ Translates provided line from local ml coord (raster indices) system to raster coordinate system
     (North America Albers Equal Area).
    Modified from IndicesToCoords.
    Destructively changes routelist in place.
    Parameters:
        raster: string, relative or abs path to raster location
        routelist: list, collection of points that form a line
    Returns:
        wgsList: list, original coordinate list translated from local coords to wgs84
    """

    ds = gdal.Open(raster)
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    for i, coord in enumerate(routelist):
        coord = (coord[-1], coord[0])
        x = coord[0] * x_size + upper_left_x + (x_size / 2)  # add half the cell size
        y = coord[1] * y_size + upper_left_y + (y_size / 2)  # to centre the point

        # Convert from Albers Equal Area to WGS 84
        wgs84_coordinates = AeaToWgs84((x, y))       #Stephen, updated function here, was NOT able to check/test

        # Note that this is returning as Y, X
        routelist[i] = (wgs84_coordinates[1], wgs84_coordinates[0])
    return routelist


#Edited line 89
def generate_line_ml(start, dest):
    """ Call machine learning functions to generate line between parameter points
       Paramters: start, dest: tuple, the start and end points of the line that will be generated, passed in as WGS84 coords
       Returns: route: list, the list of coordinates that composes the line
       """
    raspath = resource_path('raster/cost_10km_aea.tif' )

    startlocal = CoordinatesToIndices(raspath,
                                      start)  # translate WGS84 coords into local raster index coords for ML processing
    destlocal = CoordinatesToIndices(raspath, dest)
    pipecontrol = PipelineController(startlocal, destlocal)
    route_local = pipecontrol.ml_run()
    route_wgs = translateLine(raspath, route_local)
    """
    # write post-ml route list to a file for Ben to troubleshoot. Only needed for ben's troubleshooting
    with open('report_builder_input.txt','w') as f:
        for line in route_wgs:
            f.write(f"{line}\n")
    """
    return route_wgs


#NEW FUNCTION
def AeaToWgs84(aea_coords):
    """
    Apply geotransformation to reproject coordinates from North America Albers Equal Area Conic (WKT 102008) in NAD 83
    to WGS 84

    :param aea_coords: northing and easting in North America Albers Equal Area Conic
    :return: coordinates in WGS 84
    """

    # aea_wkt = 'PROJCS["North_America_Albers_Equal_Area_Conic", GEOGCS["NAD83", DATUM["North_American_Datum_1983", ' \
    #           'SPHEROID["GRS 1980",6378137,298.257222101, AUTHORITY["EPSG","7019"]], AUTHORITY["EPSG","6269"]], ' \
    #           'PRIMEM["Greenwich",0, AUTHORITY["EPSG","8901"]], UNIT["degree",0.0174532925199433, ' \
    #           'AUTHORITY["EPSG","9122"]], AUTHORITY["EPSG","4269"]], PROJECTION["Albers_Conic_Equal_Area"],' \
    #           ' PARAMETER["latitude_of_center",40], PARAMETER["longitude_of_center",-96], ' \
    #           'PARAMETER["standard_parallel_1",20], PARAMETER["standard_parallel_2",60], PARAMETER["false_easting",0], ' \
    #           'PARAMETER["false_northing",0], UNIT["metre",1, AUTHORITY["EPSG","9001"]], AXIS["Easting",EAST], ' \
    #           'AXIS["Northing",NORTH], AUTHORITY["ESRI","102008"]]'
    # wgs84_wkt = 'GEOGCS["WGS 84", DATUM["WGS_1984", SPHEROID["WGS 84",6378137,298.257223563, AUTHORITY["EPSG","7030"]], ' \
    #             'AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich",0, AUTHORITY["EPSG","8901"]], ' \
    #             'UNIT["degree",0.0174532925199433, AUTHORITY["EPSG","9122"]], AUTHORITY["EPSG","4326"]]'
    aea_epsg = 102008
    aea_epsg2 = 9822
    aea_wkt = 'PROJCS["North_America_Albers_Equal_Area_Conic",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["longitude_of_center",-96.0],PARAMETER["Standard_Parallel_1",20.0],PARAMETER["Standard_Parallel_2",60.0],PARAMETER["latitude_of_center",40.0],UNIT["Meter",1.0],AUTHORITY["Esri","102008"]]'
    wgs84_epsg = 4326

    # input spatial reference
    inSpatialReference = osr.SpatialReference()
    #inSpatialReference.ImportFromEPSG(aea_epsg1)
    inSpatialReference.ImportFromWkt(aea_wkt)


    # output spatial reference
    outSpatialReference = osr.SpatialReference()
    outSpatialReference.ImportFromEPSG(wgs84_epsg)


    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialReference, outSpatialReference)

    # run CoordinateTransformation
    wgs84_coords = coordTrans.TransformPoint(aea_coords[0], aea_coords[1])

    return wgs84_coords


#NEW FUNCTION
def Wgs84ToAea(wgs84_coords):
    """
    Apply geotransformation to reproject coordinates from WGS 84 to North America Albers Equal Area Conic (WKT 102008)
    in NAD 83

    :param wgs84_coords: coordinates in WGS 84
    :return: northing and easting in North America Albers Equal Area Conic
    """
    aea_epsg = 102008
    aea_epsg2 = 9822
    wgs84_epsg = 4326
    aea_wkt = 'PROJCS["North_America_Albers_Equal_Area_Conic",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["longitude_of_center",-96.0],PARAMETER["Standard_Parallel_1",20.0],PARAMETER["Standard_Parallel_2",60.0],PARAMETER["latitude_of_center",40.0],UNIT["Meter",1.0],AUTHORITY["Esri","102008"]]'
   
    #aea_epsg = 102008
    wgs84_epsg = 4326

    #Change the in or outSpatial Reference based on which one represents aea_wkt to say "ImportFromWkt"
    # input spatial reference
    inSpatialReference = osr.SpatialReference()
    inSpatialReference.ImportFromEPSG(wgs84_epsg)


    # output spatial reference
    outSpatialReference = osr.SpatialReference()
    #outSpatialReference.ImportFromEPSG(aea_epsg2)
    outSpatialReference.ImportFromWkt(aea_wkt)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialReference, outSpatialReference)

    # run CoordinateTransformation
    # aea_in = {wgs84_coords[0], wgs84_coords[1], 0.0} 
    # aea_coords = coordTrans.TransformPoint(wgs84_coords[1], wgs84_coords[0])
    aea_coords = coordTrans.TransformPoint(wgs84_coords[1], wgs84_coords[0])
    # aea_coords = coordTrans.TransformPoint(aea_in)

    return aea_coords


if __name__ == "__main__":

    # STEPHEN, Below are the tests that I ran, everything appeared to work. Only function not tested is
    # translateLine(raspath, route_local)

    wgs_values = [(-116.678645967999, 39.572077539),
                (-116.035197552999, 39.464836136),
                (-108.206575166999, 37.856215098),
                (-93.5145030179999, 41.073457174),
                (-93.5145030179999, 41.395181382),
                (-87.8307086839999, 36.24759406),
                (-132.121407933999, 55.872770725),
                (-144.132445018999, 63.379668904),
                (-51.8403264249999, 72.000453368),
                (-81.6877870949999, 27.229262365),
                (-72.2622731979999, 43.462091852),
                (-121.222581488999, 45.818470325),
                (-104.727932171999, 32.203839143)] #see table below for coordinate transformation testing

    for w in wgs_values:
        aea_coords = Wgs84ToAea(w)
        wgs84_coords = AeaToWgs84(aea_coords)
        print(w, wgs84_coords, aea_coords)

    raster_aea = r"C:\Users\romeolf\Desktop\cost_10km_aea\cost_10km_aea.tif"
    routelist = [(525, 471),
                (524, 472),
                (523, 473),
                (522, 474),
                (521, 475), #given as y,x
                (520, 476),
                (519, 477),
                (518, 478),
                (517, 479),
                (516, 480),
                (515, 481),
                (514, 482),
                (513, 483),
                (512, 484),
                (512, 485),
                (513, 486),
                (514, 487),
                (514, 488),
                (513, 489),
                (513, 490),
                (512, 491),
                (511, 492),
                (511, 493),
                (511, 494),
                (511, 495),
                (511, 496),
                (511, 497),
                (510, 498),
                (510, 499),
                (510, 500),
                (510, 501),
                (511, 502),
                (510, 503),
                (510, 504),
                (510, 505),
                (510, 506),
                (510, 507),
                (510, 508),
                (510, 509),
                (510, 510),
                (510, 511),
                (510, 512),
                (510, 513),
                (510, 514),
                (510, 515),
                (510, 516),
                (511, 517),
                (512, 518),
                (512, 519),
                (511, 520),
                (511, 521),
                (510, 522),
                (510, 523),
                (510, 524),
                (510, 525),
                (511, 526),
                (511, 527),
                (510, 528),
                (511, 529),
                (511, 530),
                (511, 531),
                (511, 532),
                (511, 533),
                (511, 534),
                (511, 535),
                (511, 536),
                (511, 537),
                (511, 538),
                (511, 539),
                (511, 540),
                (511, 541),
                (511, 542)]
    for r in routelist:
        print(r)
        a, b = IndicesToCoordinates(raster_aea, r)
        c, d = CoordinatesToIndices(raster_aea, (a, b))
        print(a,b,c,d)

    """Coordinates tested with from AEA (North America Albers Equal Area to WGS84 and vice-a-versa

    x_wgs84	y_wgs84	x_aea	y_aea
    -116.678646	39.57207754	-1659909.425	131294.6109
    -116.0351976	39.46483614	-1611695.001	107838.3733
    -108.2065752	37.8562151	-1010877.478	-187373.7677
    -93.51450302	41.07345717	196438.6424	129267.962
    -93.51450302	41.39518138	195442.6228	167248.1961
    -87.83070868	36.24759406	693829.4208	-411580.4196
    -132.1214079	55.87277073	-2140915.471	2275737.737
    -144.132445	63.3796689	-2391902.761	3320871.753
    -51.84032642	72.00045337	1823646.181	3992349.845
    -81.68778709	27.22926237	1369671.566	-1383287.996
    -72.2622732	43.46209185	1786819.668	633813.1642
    -121.2225815	45.81847033	-1822798.78	931333.4709
    -104.7279322	32.20383914	-784549.8711	-877454.8434

    """

    def test_ml():
        """ Dummy function to test point translation and ml function without needing to interact with frontend
        """
        raspath = resource_path('raster/ras_10km_resampled_071323_WGS84.tif')

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


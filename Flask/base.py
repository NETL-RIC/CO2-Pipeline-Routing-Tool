"""
base
Contains all major endpoints for the server, and the Flask() object that controls them
"""
import os.path
import os
import sys
import webbrowser
from pathlib import Path
from datetime import timedelta

import shutil
import glob
from flask import Flask, request, render_template, send_file, session
from flask_apscheduler import APScheduler
import fiona
import torch
from osgeo import gdal, ogr, osr
import numpy as np
import uuid
import zipfile

from controller import PipelineController
from line_builder import line_builder
from report_builder.report_builder import report_builder
from extra_utils import resource_path

api = Flask(__name__, 
            static_url_path='', 
            static_folder=resource_path('build'), 
            template_folder=resource_path('build'))

api.secret_key = 'BAD_SECRET_KEY'
api.config["SESSION_PERMANENT"] = False
api.config["SCHEDULER_API_ENABLED"] = True

# Runs scheduler to remove old session folders ever 24 hours
scheduler = APScheduler()
scheduler.init_app(api)
scheduler.start()

# Differences between bundled (exported as .exe) and webtool mode
if getattr(sys, 'frozen', False):
    APP_ROOT = os.path.dirname(sys.executable)
elif __file__: #If tool is in bundled/exe mode
    APP_ROOT = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'user_uploads')

# Schedule session folder cleanup to remove stray folders that weren't handled by the window.beforeUnload trigger
@scheduler.task('interval', id='delete_old_folders', hours=24)
def delete_old_folders():
    """ Remove the contents of Flask/sessions every 24 hours
    """
    sessions_dir = resource_path('sessions')
    if not os.path.isdir(sessions_dir):
        api.logger.info("Sessions folder doesn't exist for daily scheduled deletion")
    
    for item in os.listdir(sessions_dir):

        item_path = os.path.join(resource_path(sessions_dir), item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)    # remove files and symlinks
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)    # remove folders recursively
        except OSError as e:
            api.logger.error("\tError clearing contents of sessions folder")

@api.route('/token', methods=['GET', 'POST'])
def a():
    """Endpoint for generating line shapefiles and report
    Parameters: none
    Returns: route: line, the generated line in wgs84 to be plotted in the browser
    """
    if request.method == 'POST':
        start = request.json.get("s", None)
        end = request.json.get("e", None)
        api.logger.info(
            f"Start: {start}"
            f"End: {end}"
        )
        mode = request.json.get("mode", None)
        route = generate_line_ml(start, end, mode)    # calculate line with ML
        api.logger.info("Pipeline generated")

        first_point = route[0]
        last_point = route[-1]  

        out_dir = resource_path("sessions\\" + session.get('uid'))

        if os.path.exists(out_dir):
            delete_dir_contents(out_dir)   # delete output from a previous run in this same session
        else:
            os.mkdir(out_dir)

        shpinfo = line_builder(route, out_dir)  # create shapefile(s) in ./output, based on line, return filename of output .shp file
        output_shp_abspath = shpinfo[1]
        output_shp_filename = shpinfo[0]
       
        pdf_name = report_builder(output_shp_abspath, first_point, last_point, out_dir)    # create pdf report in './output
        # delete_prev_zips_pdfs()                   # delete zip from last run if exist
        zip_path = create_output_zip(output_shp_filename) # create zip of pdf/shp files in session folder
        api.logger.info("Output zip created")

        route_correct_swap = []
        for coord in route:
            route_correct_swap.append((coord[1], coord[0]))
            
        return {'route': route_correct_swap, 'zip':zip_path}

@api.route('/download_report', methods=['POST'])
def send_report():
    """API Endpoint for sending appropriate file to the front end.
    """
    public_f = resource_path('sessions\\' + session.get('uid'))
    if request.method == 'POST':
        ext = request.json.get("extension", None)
        try:
            if ext == '.pdf':
                file_path = os.path.join(public_f, 'route_report.pdf')  
                os.path.exists(file_path)
                return send_file(file_path, as_attachment=True, download_name='route_report.pdf')
            elif ext == '.zip':
                file_path = os.path.join(public_f, 'route_shapefile_and_report.zip')
                os.path.exists(file_path)
                return send_file(file_path, as_attachment=True, download_name='route_shapefile_and_report.zip')
            else:
                api.logger.error(f"file extension provided: {ext} is not handled.")
                return "Invalid file extension provided", 404
        except FileNotFoundError:
            api.logger.error("unable to locate requested filetype")
            return f"{ext} file not found", 404

def create_output_zip(zipname):
    """ Creates a zip file in the uid-specific sessions directory
    Params: zipname - the name of the zip file to be created
    Returns: dest_path - the full path of where the new zip was placed
    """
    def zipdir(path, ziph, zipname):
        for root, dirs, files, in os.walk(path):
            files.remove(zipname)  # remove the zip from the files to be included in the zip lol
            for file in files:

                if file != zipname:
                    ziph.write(os.path.join(root, file))
    
    zipname = 'route_shapefile_and_report.zip'    
    try:
        dl_f = resource_path('sessions\\' + session.get('uid'))
    except Exception as e:
        api.logger(e)

    dest_path = os.path.join(dl_f, zipname)

    # copy the reference sheet pdf into the folder that will be zipped up
    shutil.copy(resource_path('other_assets/reference_sheet.pdf'), dl_f)
    print(os.getcwd())
    #shutil.make_archive(dest_path, 'zip', dl_f)

    with zipfile.ZipFile(f"sessions\\{session.get('uid')}\\{zipname}", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir("sessions\\" + session.get('uid'), zipf, zipname)

    api.logger.info(f"\tCreated download zipfile at {dest_path}")
    return dest_path

@api.route('/gen_uid')
def index():
    """ Generate a user id unique to the user's session and send it back to the browser
    Returns: 204 code (success, nothing to return) for the browser
    """
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid4())
    print(session['uid'])
    # Don't need to send uid to client, return 204 (succcess, no content)
    return ("", 204)

@api.route('/profile')
def my_profile():
    """ Returns profile information of the tool 
    Returns:
        response_body - returns an object with the tool's name and a very brief 'about' section
    """
    response_body = {
        "name": "CO2 Pipeline Routing App",
        "about": "Web app to generate CO2 Pipelines across the USA and Alaska"
    }
    return response_body

@api.route('/help', methods = ['POST'])
def open_help():
    """ Open the help docs in the user's native browser
    Returns: h_path: the path where the help docs are
    """
    h_path = resource_path("documentation/_build/html/index.html")
    webbrowser.open(f"file://{h_path}")
    return(h_path)

# Evaluate button 
@api.route('/uploads', methods = ['POST'])
def uploads_file():
    """ Runs the 'evaluate' mode of the tool, generating a pdf report based on user-uploaded shapefiles of an area or route (polygon or line)
    Returns: path to the generated report
    """
    try:
        delete_dir_contents(resource_path('user_uploads'))     #clear out stuff from a previous tool run
    except PermissionError as e:
        api.logger.error("Permission Error,", e)
    name = ''
    file = request.files
    for i in file:
        name = file[i].filename
        # file[i].save(os.path.join(UPLOAD_FOLDER, name))
        # cur_dir = os.path.dirname(__file__)
        file_path = os.path.join(resource_path('user_uploads'), name)
        file[i].save(file_path)
    
    ret = []
    c = fiona.open(file_path)
    shptype = c.schema["geometry"]
    
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

    pdf_path = None
    if shptype == "LineString":
        api.logger.info("Creating PDF report for LineString shapefile...")
        # first_point = v['array'][0] # unnessecary right now, but in case it's needed later
        # last_point = v['array'][-1] # unnessecary right now, but in case it's needed later
        pdf_path = run_line_eval_mode()
    elif shptype == "Polygon":
        api.logger.info("Creating PDF report for Polygon shapefile...")
        pdf_path = run_line_eval_mode()
    else:
        api.logger.error("Uploaded shapefile is neither a polygon or a line. Please upload an appropriate shapefile")
    
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
    if shp_extension_file == None:
        api.logger.error("No .shp file found in user_uploads")
        return None
    else:
        output_shp_abspath = os.path.join(resource_path("user_uploads"), shp_extension_file)
        delete_prev_zips_pdfs()
        public_abspath = resource_path('public')
        if not os.path.exists(public_abspath):
            os.mkdir(public_abspath)
            api.logger.info(f"Created public folder at {public_abspath} (none existed)")
        pdfname = report_builder(shapefile=output_shp_abspath, out_path=public_abspath)    # create pdf report in '../public' so front-end can grab it easily
        api.logger.info("Created pdf report")
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
    if (len(os.listdir((rel_path)))) != 0:
        rel_path = os.path.abspath(rel_path)
        rel_path  = rel_path +'/*'
        files = glob.glob(rel_path)
        count = 0
        for f in files:
            os.remove(f)
            count = count + 1

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
                os.remove(os.path.join(public_path, file))
@api.route('/get_uid', methods=['GET'])
def send_id():
    """ Send session id
    """
    uid = session.get('uid')
    print(uid)
    return {'uid': uid}


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

def generate_line_ml(start, dest, mode):
    """ Call machine learning functions to generate line between parameter points
       Paramters: start, dest: tuple, the start and end points of the line that will be generated, passed in as WGS84 coords
       Returns: route: list, the list of coordinates that composes the line
       """

    api.logger.info("Generating pipeline...")

    raspath = resource_path('raster/cost_10km_aea.tif' )

    startlocal = CoordinatesToIndices(raspath, start)  # translate WGS84 coords into local raster index coords for ML processing
    destlocal = CoordinatesToIndices(raspath, dest)

    pipecontrol = PipelineController(startlocal, destlocal, mode)

    route_local = pipecontrol.ml_run()
    route_wgs = translateLine(raspath, route_local)

    return route_wgs

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

#----Logging------

def before_request_logging():
    """Logging function for request info before sending
    """
    if not (request.url.endswith('_reload-hash')): # skip dash's refresh
        user_agent = request.user_agent.string
        api.logger.info(f"Request: {request.method}, {request.url} from IP: {get_client_ip()}, User-Agent: {user_agent}")

def after_request_logging(response):
    """Logging function for request responses
    :param response: The response from the server to the request
    :return: The response from the server to the request
    """
    httpcode = response.status_code
    if httpcode < 200: # informational responses
        user_agent = request.user_agent.string
        api.logger.info(f"IP: {get_client_ip()}, User-Agent: {user_agent}, Status: {response.status}")

    elif httpcode >= 200 and httpcode < 300: #successful responses
        api.logger.info(f"Successful response, {httpcode}. IP: {get_client_ip()}, Status: {response.status}")

    elif httpcode >= 300 and httpcode < 400: #Redirection responses
        api.logger.warning(f"Redirection response, {httpcode}. IP: {get_client_ip()}, Status: {response.status}")

    elif response.status_code >= 400: # Error responses
        api.logger.error(f"Error response, {httpcode}, IP: {get_client_ip()}, Status: {response.status}")
        api.logger.debug(f"Response body: {response.get_data}")
    return response

def exception_logging(e):
    """Logging function for errors
    :param e: The error message to log
    """
    api.logger.error(
        f"Exception:"
        f"IP: {get_client_ip()}"
        f"Method: {request.method}"
        f"Path: {request.path}"
        f"Error: {str(e)}"
        f"User-Agent: {request.user_agent}"
        f"Response Headers: {request.get_wgsi_headers}"
    )
    raise e

def get_client_ip():
    """ Supporting function that gets client IP for other logging functions
    :return: The IP that the request came from
    """
    return request.headers.get('X-Forwarded For', request.remote_addr)

@api.route('/window_close', methods=['GET'])
def remove_session_state():
    uid = session.get('uid')
    if uid is not None:
            if os.path.exists("sessions/" + uid):
                try:
                    shutil.rmtree("sessions/" + uid)
                except Exception as e:
                    api.logger.error(f"Error removing folder sessions/{uid}: {e.stderror}")
            else:
                api.logger.error(f"Folder sessions/{uid} doesn't exist when attempting to delete")
    else:
        api.logger.error("Could not get uid for this session")
    api.logger.info(f"\n\t Session {uid}  folder removed upon browser close")
    return ("", 204)



# Register logging functions
api.before_request(before_request_logging)
api.after_request(after_request_logging)
api.errorhandler(exception_logging)

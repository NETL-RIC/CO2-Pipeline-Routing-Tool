"""
line_builder 
Creates an output shapefile for the generated pipeline data
"""

import os
from osgeo import ogr, osr
from datetime import datetime
from extra_utils import resource_path

def get_file_name(file_path):
    """ Gets filename (no extension) from path with \\ not /
    """
    file_path_split = file_path.split('\\')
    file_name_and_extension = file_path_split[-1].rsplit('.', 1)
    return file_name_and_extension[0]

def CleanDatetime(datestring):
    """
    Replace unwanted characters in string with an underscore as needed

    :param string: in value
    :return: in value with replaced characters
    """
    replacements = [" ", "-", ":"]
    for r in replacements:
        datestring = datestring.replace(r,'_')

    if "." in datestring:
        datestring = datestring.split(".")[0]

    return(datestring)

def line_builder(coords, out_dir):
    """
    Creates a line shapefile in WGS84
    :param coords: list of coordinates as tuples in WGS 84
    :param out_dir: the session-specific output folder to save the shapefiles to
    :return:
    """
    # Set line geometry
    line = ogr.Geometry(ogr.wkbLineString)
    for c in coords:
        line.AddPoint(c[0], c[1])
    driver = ogr.GetDriverByName('Esri Shapefile')
    out_shp = resource_path(out_dir)     # name of dir to save shapefiles to
    out_shp = os.path.join(out_shp, f"route_{CleanDatetime(str(datetime.now()))}.shp")
    ds = driver.CreateDataSource(out_shp)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326) #WGS84
    lyr = ds.CreateLayer(out_shp, srs, geom_type=ogr.wkbLineString)
    # Add an ID field
    idField = ogr.FieldDefn("id", ogr.OFTInteger)
    lyr.CreateField(idField)
    # Create the feature and set values
    featureDefn = lyr.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(line)
    feature.SetField("id", 1)
    lyr.CreateFeature(feature)
    feature.Destroy()
    ds.Destroy()
    out_shp_abspath = out_shp
    out_shp_filename = get_file_name(out_shp_abspath)
    return [out_shp_filename, out_shp_abspath]

def line_builder_old(coords):
    """
    Creates line shapefiles in WGS84 and saves to Flask/output_shapefiles
    These are used by the PDF report builder, and turned into a zip for user-download in _____

    :param coords: list of coordinates as tuples in WGS 84
    :return: out_shp: string with 'output_shapefiles' + name of the file
    """
    # Set line geometry
    line = ogr.Geometry(ogr.wkbLineString)
    for c in coords:
        line.AddPoint(c[1], c[0])

    out_shp = os.path.abspath("output")     # name of dir to save shapefiles to
    out_shp = os.path.join(out_shp, f"route_{CleanDatetime(str(datetime.now()))}.shp")
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326) #WGS84

    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(out_shp)
    lyr = ds.CreateLayer(out_shp, srs, geom_type=ogr.wkbLineString)

    featureDefn = lyr.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(line)
    lyr.CreateFeature(feature)

    ds.Destroy()

    out_shp_abspath = out_shp
    out_shp_filename = get_file_name(out_shp_abspath)
    return [out_shp_filename, out_shp_abspath]
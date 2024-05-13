"""
Author: Lucy Romeo
Given raster grid, run the least cost paths between points
https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
"""

import os
from osgeo import gdal, ogr, osr
from skimage.graph import route_through_array
import numpy as np
import csv
from zipfile import ZipFile

wkt_srs = 'PROJCS["North_America_Equidistant_Conic",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Equidistant_Conic"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",20.0],PARAMETER["Standard_Parallel_2",60.0],PARAMETER["Latitude_Of_Origin",40.0],UNIT["Meter",1.0]]'


def wgs842wktsrs(coordinates):

    """
    Reproject vector from WGS84 datum (EPSG 4326)
    to US Contiguous Equidistant Conic (wkt text above))
    :param vector: point vector
    :return: transformed vector
    """

    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)

    target = osr.SpatialReference()
    target.ImportFromWkt(wkt_srs)

    transform = osr.CoordinateTransformation(source, target)
    return transform.TransformPoint(float(coordinates[0]), float(coordinates[1]))


def convertCoordToShp(locations, tmp):

    """
    Convert coordinates to a shapefile and save to
    memory driver. Utilizes code from https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html

    :param coords: list of coordinates in wkt_srs spatial reference system
    :return: path to point shapefile
    """

    # create an output datasource in memory
    out_driver = ogr.GetDriverByName('ESRI SHAPEFILE')

    # output path join
    source = out_driver.CreateDataSource(os.path.join(tmp, "end_location.shp"))
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt_srs)

    out_layer = source.CreateLayer("end_location", srs, geom_type=ogr.wkbPoint)
    id_fld = ogr.FieldDefn("id", ogr.OFTInteger)
    out_layer.CreateField(id_fld)

    for l in locations:
        feature_defn = out_layer.GetLayerDefn()
        feature = ogr.Feature(feature_defn)
        point = ogr.CreateGeometryFromWkt(f"POINT ({l[0]} {l[1]})")
        feature.SetGeometry(point)
        feature.SetField("id", 0)
        out_layer.CreateFeature(feature)

    source.FlushCache()

    return(os.path.join(tmp, "end_location.shp"))


def rasterizeVectorLayer(vector, raster_ds, tmp):

    """
    Convert ogr layer to a raster, scripts partially from
    https://gis.stackexchange.com/questions/212795/rasterizing-shapefiles-with-gdal-and-python

    :param vector: point layer
    :return: raster surface representing input vector
    """

    geo_transform = raster_ds.GetGeoTransform()
    # Pull raster details
    x_min = geo_transform[0]
    y_max = geo_transform[3]
    x_max = x_min + geo_transform[1] * raster_ds.RasterXSize
    y_min = y_max + geo_transform[5] * raster_ds.RasterYSize
    x_res = raster_ds.RasterXSize
    y_res = raster_ds.RasterYSize
    pixel_width = geo_transform[1]

    vector_ds = ogr.Open(vector)
    lyr = vector_ds.GetLayer()

    out_raster = os.path.join(tmp, "end_location.tif")
    target_ds = gdal.GetDriverByName("Gtiff").Create(out_raster, x_res, y_res, 1, gdal.GDT_Byte)
    target_ds.SetProjection(raster_ds.GetProjection())
    target_ds.SetGeoTransform((x_min, pixel_width, 0, y_min, 0, pixel_width))
    band = target_ds.GetRasterBand(1)
    NoData_value = 0
    band.SetNoDataValue(NoData_value)
    band.FlushCache()

    gdal.RasterizeLayer(target_ds, [1], lyr)
    target_ds.FlushCache()

    return(target_ds)


def getRasterDatasource(raster):

    """
    Returns raster datasource from raster file
    :param raster: raster file
    :return: raster datasource
    """

    return(gdal.Open(raster))


def calculateCostDistance(raster_ds, tmp):

    """
    Convert in_raster to a cost distance raster

    :param in_raster: in raster datasource representing vector (1)
     v no vector (0.0) presence
    :return: cost distance raster
    """

    raster_driver = gdal.GetDriverByName("GTiff")
    # raster_ds = gdal.Open(in_raster)
    src_band = raster_ds.GetRasterBand(1)

    geo_transform = raster_ds.GetGeoTransform()
    # Pull raster details
    x_min = geo_transform[0]
    y_max = geo_transform[3]
    x_max = x_min + geo_transform[1] * raster_ds.RasterXSize
    y_min = y_max + geo_transform[5] * raster_ds.RasterYSize
    x_res = raster_ds.RasterXSize
    y_res = raster_ds.RasterYSize
    pixel_width = geo_transform[1]

    dist_raster = os.path.join(tmp, "cost_distance.tif")
    dst_ds = raster_driver.Create(dist_raster, x_res, y_res, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(raster_ds.GetGeoTransform())
    dst_ds.SetSpatialRef(raster_ds.GetSpatialRef())
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.SetNoDataValue(np.inf)

    gdal.ComputeProximity(src_band, dst_band,
                          options=["DISTUNITS=GEO"])

    # do some corrections
    buffer = dst_band.ReadAsArray()
    rbuff = buffer.ravel()
    # replace nodatas with 0 distance
    rbuff[rbuff == np.inf] = 0.0

    dst_band.WriteArray(buffer)

    # TODO: only complete for one point, not both
    dst_ds.FlushCache()
    # print(dist_raster)
    return(dst_ds)


def multiplyRasters(raster_1, raster_2, tmp):

    """
    Multiply together raster_1 and raster_2
    :param in_rasters: List of raster data sources
    :return: Product raster
    """

    band_1 = raster_1.GetRasterBand(1)
    arr_1 = band_1.ReadAsArray()

    band_2 = raster_2.GetRasterBand(1)
    arr_2 = band_2.ReadAsArray()

    # Attempt to limit zero issue
    arr_1[arr_1 < 0] = 999999999  # Previously 0  # Remove negative values
    arr_2[arr_2 == 0] = 0.001  # TODO: adjust to the minimum value above 0, prevent multiplication from causing 0 issue
    arr_2[arr_2 < 0.001] = 999999999  # TODO: Adjust to a high value to weight away from nulls

    product = np.float64(arr_1) * np.float64(arr_2)
    product[product <= 0] = 999999999  # TODO: Adjust to high value to weight away from nulls

    # Write to output
    geotransform = raster_2.GetGeoTransform()
    spatial_reference = raster_2.GetSpatialRef()
    x_res = raster_2.RasterXSize
    y_res = raster_2.RasterYSize

    output = os.path.join(tmp, "cost_surface.tif")
    raster_driver = gdal.GetDriverByName("GTiff")
    out_ds = raster_driver.Create(output, x_res, y_res, 1, gdal.GDT_Float64)
    out_ds.SetGeoTransform(geotransform)
    out_ds.SetSpatialRef(spatial_reference)
    out_ds.GetRasterBand(1).WriteArray(product)

    out_ds.FlushCache()

    return(out_ds)


def raster2array(raster):

    # raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()

    return array


def coord2pixelOffset(raster, x, y):

    # raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    xOffset = int((x - originX)/pixelWidth)
    yOffset = int((y - originY)/pixelHeight)
    return xOffset, yOffset


def createPath(CostSurfacefn, costSurfaceArray, startCoord, stopCoord):

    # coordinates to array index
    startCoordX = startCoord[0]
    startCoordY = startCoord[1]
    startIndexX, startIndexY = coord2pixelOffset(CostSurfacefn, startCoordX, startCoordY)

    stopCoordX = stopCoord[0]
    stopCoordY = stopCoord[1]
    stopIndexX, stopIndexY = coord2pixelOffset(CostSurfacefn, stopCoordX, stopCoordY)

    # create path
    indices, weight = route_through_array(costSurfaceArray, (startIndexY, startIndexX), (stopIndexY, stopIndexX), geometric=True, fully_connected=True)
    # indices, weight = skimage.graph.shortest_path(costSurfaceArray, reach=1, )
    # TODO: Try code used here: https://stackoverflow.com/questions/54484510/minimum-cost-path-least-cost-path
    # potentially try this which uses rasterio: https://www.linkedin.com/pulse/least-cost-path-analysis-algorithm-chonghua-yin

    indices = np.array(indices).T
    path = np.zeros_like(costSurfaceArray)
    path[indices[0], indices[1]] = 1
    return path


def array2raster(raster, tmp, raster_name, array):
    # raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(os.path.join(tmp, raster_name), cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


def pixelOffset2coord(raster, xOffset,yOffset):
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    coordX = originX+pixelWidth*xOffset
    coordY = originY+pixelHeight*yOffset
    return coordX, coordY


def raster2point(raster, array, output_location, output):
    """
    Converts a raster to point shapefile where value of raster are greater than 0 (value == 1)

    """
    # TODO: complete!
    #https://gis.stackexchange.com/questions/340284/converting-raster-pixels-to-polygons-with-gdal-python
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt_srs)

    in_raster = gdal.Open(raster)

    ogr_ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(os.path.join(output_location, f"{output}"))
    out_layer = ogr_ds.CreateLayer(os.path.join(output_location, f"{output}"), srs)

    field_defn = ogr.FieldDefn("ID", ogr.OFTInteger)
    out_layer.CreateField(field_defn)
    field_defn = ogr.FieldDefn("WEIGHT", ogr.OFTReal)
    out_layer.CreateField(field_defn)

    featureDefn = out_layer.GetLayerDefn()

    point = ogr.Geometry(ogr.wkbPoint)
    for ridx, row in enumerate(array):
        for cidx, value in enumerate(row):
            if value > 0:
                Xcoord, Ycoord = pixelOffset2coord(in_raster, cidx, ridx)
                point.AddPoint(Xcoord, Ycoord)
                outFeature = ogr.Feature(featureDefn)
                outFeature.SetGeometry(point)
                out_layer.CreateFeature(outFeature)
                outFeature.SetField("ID", outFeature.GetFID())
                out_layer.SetFeature(outFeature)
                outFeature.Destroy()

    del ogr_ds, out_layer


def values2point(cost_raster, point_shp, out_path):
    """
    Extract values by point locations from input cost_raster

    :param cost_raster: cost surface raster
    :param point_shp: point layer shapefile
    # Sourced from https://gis.stackexchange.com/questions/46893/getting-pixel-value-of-gdal-raster-under-ogr-point-without-numpy/46898#46898
    """
    src_ds = gdal.Open(cost_raster)
    geo_transform = src_ds.GetGeoTransform()
    band = src_ds.GetRasterBand(1)

    shp = ogr.Open(point_shp)
    shp_lyr = shp.GetLayer()

    values = list()
    for feat in shp_lyr:
        geom = feat.GetGeometryRef()
        feat_id = feat.GetField('ID')
        mx, my = geom.GetX(), geom.GetY()

        px = int((mx - geo_transform[0]) / geo_transform[1])
        py = int((my - geo_transform[3]) / geo_transform[5])

        intval = band.ReadAsArray(px, py, 1, 1)
        values.append((feat_id, float(intval)))

    with open(os.path.join(out_path,'summary.csv'),'w',newline='') as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=['ID','WEIGHT'])
        for v in values:
            writer.writerow({'ID':v[0], 'WEIGHT':v[1]})


def raster2contour(raster, output_location, output):
    """
    Convert raster to polyline using gdal contourgenerate function
    """
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt_srs)

    in_raster = gdal.Open(raster)
    in_band1 = in_raster.GetRasterBand(1)

    ogr_ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(os.path.join(output_location, f"{output}"))
    contour_shp = ogr_ds.CreateLayer(os.path.join(output_location, f"{output}"), srs)

    field_defn = ogr.FieldDefn("ID", ogr.OFTInteger)
    contour_shp.CreateField(field_defn)
    field_defn = ogr.FieldDefn("WEIGHT", ogr.OFTReal)
    contour_shp.CreateField(field_defn)

    gdal.ContourGenerate(in_band1, 1, 0, [], 0, 0, contour_shp, 0, 1)

    del ogr_ds, contour_shp


def prj2wgs84(inshp, outshp):
    """
    Reproject inshp to outshp, resulting projection in WGS84
    Built off of code here: https://pcjericks.github.io/py-gdalogr-cookbook/projection.html
    """
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # get the input layer
    in_ds = driver.Open(inshp)
    in_lyr = in_ds.GetLayer()

    # Define input and output projections
    source = in_lyr.GetSpatialRef()
    try:
        source.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    except:
        pass
        print('ERROR')


    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)
    try:
        target.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    except:
        pass
        print('ERROR')

    # create the CoordinateTransformation
    coordinate_transformation = osr.CoordinateTransformation(source, target)

    # create the output layer
    if os.path.exists(outshp):
        driver.DeleteDataSource(outshp)
    out_ds = driver.CreateDataSource(outshp)
    out_lyr = out_ds.CreateLayer(outshp, target, geom_type=ogr.wkbLineString)

    # add fields
    in_lyr_dfn = in_lyr.GetLayerDefn()
    for i in range(0, in_lyr_dfn.GetFieldCount()):
        fld_dfn = in_lyr_dfn.GetFieldDefn(i)
        out_lyr.CreateField(fld_dfn)

    # get the output layer's feature definition
    out_lyr_dfn = out_lyr.GetLayerDefn()

    # loop through the input features
    in_feature = in_lyr.GetNextFeature()
    while in_feature:
        # get the input geometry
        geom = in_feature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordinate_transformation)
        # create a new feature
        out_feature = ogr.Feature(out_lyr_dfn)
        # set the geometry and attribute
        out_feature.SetGeometry(geom)
        for i in range(0, out_lyr_dfn.GetFieldCount()):
            out_feature.SetField(out_lyr_dfn.GetFieldDefn(i).GetNameRef(), in_feature.GetField(i))
        # add the feature to the shapefile
        out_lyr.CreateFeature(out_feature)
        in_feature = in_lyr.GetNextFeature()

    # Save and close the shapefiles
    del in_ds, out_ds


def leastCostPath(sourcelat, sourcelong, destlat, destlong, cost_surface, output):

    """
    Find the least cost path from source to sink, given a weighted cost surface (hex grid), points in WGS84
    :param sourcelat: start latitude
    :param sourcelong: start longitude
    :param destlat: destination latitude
    :param destlong: destination latitude
    :param path: directory path to save results to
    :return: selected hexgrids of the least cost path
    """
    sourcelat = float(sourcelat)
    sourcelong = float(sourcelong)
    destlat = float(destlat)
    destlong = float(destlong)
    output_path = '.'
    print(destlat)
    # print(sourcelat, sourcelong, destlat, destlong, output_path, cost_surface, output)

    # Geotransform lat lon into equidistant conic projection for US
    # Requirement: lat lon are in WGS84
    sink_prj = wgs842wktsrs((destlat, destlong))
    source_prj = wgs842wktsrs((sourcelat, sourcelong))

    # Convert sink_prj and source_prj to shapefile


    pnt_shp = convertCoordToShp([sink_prj], output_path)
    cost_surface_ds = getRasterDatasource(cost_surface)

    #Rasterize lat and lon
    #TODO: make sure destination point raster spatially aligns with the original destination point
    pnt_ras = rasterizeVectorLayer(pnt_shp, cost_surface_ds, output_path)

    # Calculate cost distance from rasterized point destination
    cost_distance = calculateCostDistance(pnt_ras, output_path)

    # Multiply cost distance and cost surface rasters, convert product (lcp_surface) to array (lcp_surface_array)
    # TODO: clip raster by us states to limit path from going external into null values
    lcp_surface = multiplyRasters(cost_distance, cost_surface_ds, output_path)
    lcp_surface_array = raster2array(lcp_surface)

    # Create least cost path and convert to raster
    path_array = createPath(lcp_surface, lcp_surface_array, source_prj, sink_prj)
    array2raster(lcp_surface, output_path, output, path_array)

    # Convert raster output to points to pull values by location to a CSV
    raster2point(os.path.join(output_path, output), path_array, output_path, output.replace('.tif','_pnt.shp'))
    values2point(cost_surface, os.path.join(output_path, output.replace('.tif','_pnt.shp')), output_path)

    # Convert raster output to polyline as the final output shapefile
    raster2contour(os.path.join(output_path, output), output_path, output.replace('.tif', '_pre_line.shp'))
    prj2wgs84(os.path.join(output_path, output.replace('.tif', '_pre_line.shp')), os.path.join(output_path, output.replace('.tif', '_line.shp')))


    return os.path.join(output_path, output.replace('.tif', '_line.shp'))

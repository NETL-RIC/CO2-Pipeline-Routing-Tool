# Operation
The CO2 Pipeline-Routing Tool has two primary modes: Identification and Evaluation. 
Identification mode allows the user to select two points, generate a proposed pipeline route, and download a shapefile of the route and relevant PDF report on route details.
Evaluation mode allows the user to upload a shapefile of an existing route, and generate a PDF report on route details.

# Identification Mode

# Evaluation Mode

## Point Selection
There are three ways to input a start or end point on the map:
* Select `Start` or `End` respectively from the left sidebar, and click anywhere on the map.
* Enter a lat/long WGS84-compliant coordinate in the relevant text field and click `Save Start` or `Save Destination`
* Or selecting popular locations from the dropdown menu `Select Known CCS Project As Location`

These options may be mixed and matched between start point and end point (for example, you may create a start point by clicking on the map area, and your end point by using the dropdown menu). The start point will be denoted in the map area by a black Google Maps-style pin, and the destination by a red one

:::{tip}
A point's apparent location on the map and lat/long information will not be updated until the `Save Start` or `Save Destination` is selected. (When specifying a point via Lat/Long or Optional Location).
:::

## Generate Pipeline
If you are satisfied with your selected, click `Generate Pipeline` to execute the path-generation sequence of the program. The result will be a machine-learning-generated green line displayed on the map portion of the page. The page may be interacted with by dragging and scrolling with the mouse,
similar to Google Maps.

***
# Retrieve and Review Results (Forthcoming Webtool Feature)
When the program has completed running, eight different files will be exported to the output directory specified earlier. This concludes the program's path creation functionality; new start and end points may be selected, or you may safely exit the program by closing the window conventionally. What follows is an explanation of each individual ouptut file.

## end_location.shp
Shapefile of the end location (sink) in the North America Equidistant Conic projected coordinate system.

## cost_distance.tif
Distance raster showing distance (in meters) from the sink location in the North America Equidistant Conic projected coordinate system.

## cost_surface.tif
Product of the original weighteds surface (fed on the backend of the tool), multiplied by the cost_distance.tif raster surface. This raster is also in the North America Equidistant Conic projected coordinate system. 
:::{note}
Initial runs use solely the state regulations layer; future versions will use a more comprehensive weighted surface based on the data within the input geodatabase (Schooley et al. 2023).
:::

## result.tif
Binary raster representing least cost path where raster grid value equals 1. This raster is in the North America Equidistant Conic projected coordinate system. 

## result_pnt.shp
Least cost path, as a conversion from the result.tif to point shapefile, where the result.tif grid value equals 1. This shapefile is in the North America Equidistant Conic projected coordinate system.

## summary.csv
Table of weighted values crossed, based on where result_pnt.shp overlaps with the original weighted surface. 

## result_pre_line.shp 
Least cost path, as a conversaion from result.tif toa line shpaefile, where the result.tif grid value quals 1. The shapefile is in the North American Equidistant Conic projected coordinate system. 

## result_pre_line.shp
Least cost path, as a conversion from result.tif to a line shapefile, where the result.tif grid value equals 1. This shapefile is in the North America Equidistant Conic projected coordinate system. 

## result_line.shp
Least cost path, as a conversion from result.tif to a line shapefile, where the result.tif grid value equals 1. This shapefile is in the World Geodetic System 1984 geographic coordinate system. 


# Operation
The CO2 Pipeline-Routing Tool has two primary modes: Identification and Evaluation. 
Identification mode allows the user to select two points, generate a proposed pipeline route, and download a shapefile of the route and relevant PDF report on route details.
Evaluation mode allows the user to upload a shapefile of an existing route, and generate a PDF report on route details.

# Identification Mode
To start evaluation mode, click on the `Identify Route` radio button below the map. This enables all Identification Mode buttons and fields that are otherwise greyed-out.

## Start and End Points
There are two ways to enter the start and end points of the desired pipeline route.

### Clicking On The Map
Select `Start` or `End` radio button, and then click on the map to place a marker representing the chosen type of point. 

Selecting `Start` and clicking on the map will create a black marker to represent the point. 

Selecting `End` and clicking on the map will create a red marker to represent the end of the pipeline route.

:::{tip}
You do not need to click the `Save Start` button, as those are only for entering points manually via coordinates.
:::

### Entering Coordinates
You may also enter pipeline start and end points via the Latitude and Longitude World Geodetic System 1984 (WGS84) coordinates. 

The `Start` point, or the beginning of the proposed pipeline, can be created by entering the coordinate in the first pair of Latitude and Longitude text boxes, and clicking the `Save Start` button. This will create a black marker on the map to represent the point.

The `End` point can similarly be created by entering the coordinate components in the relevant fields and clicking the `Save Destination` button. This will create a red marker on the map to represent the end point.

### Selecting Known Locations
Alternatively, you may select a point from the `Select known CCS project as start` or `end` location dropdown menus. Selecting a location from either of these will create a black or red marker on the map, for start and end points respectively. 

:::{tip}
You do not need to select `Save Points` as that button is only for manual coordinate entry via the text fields above the dropdown menu. Selecting a location from the dropdown menu will save the point automatically.
:::

## Generate Pipeline
If you are satisfied with your selected points, click `Generate Pipeline` to execute the path-generation sequence of the program. The result proposed route displayed as a red line on the map, and a zip file containing a shapefile of the route and a relevant report. The map may be scaled and moved with by dragging and scrolling with the mouse, similar to Google Maps.

## Download Report 
After the Generate Pipeline button has been pressed, the tool will create two kinds of outputs, that can be downloaded by clicking the `Download Report and Shapefile` button. The first is the proposed route displayed on the map, and the second is a downloadable zip file containing:
*A shapefile representing the proposed line
*A PDF report outlining relevant statistics and details of the generated line

# Evaluation Mode
To initiate evaluation mode, click on the `Evaluate Corridor` radio button directly beneath the map. This will enable the otherwise greyed-out Evaluation Mode buttons to be interacted with.

## Upload Shapefile
To upload a shapefile for evaluation, click the `Choose Files` button, select the desired shapefile in the new file explorer window, and click "Open". Sucessfully uploaded files will be represented with a filecount directly to the right of the Choose Files button.

Once files are uploaded, click `Evaluate` to run the evaluation portion of the tool and generate a PDF report about your shapefile.

## Download Report
Clicking `Download Report` will open a file-saving window where you'll choose a destination for the PDF report and click "Save".

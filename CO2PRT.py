"""
'main' file outside of module to help pyinstaller build an exe and run the flask service

    Builds from inside the module cause issues with relative imports.
    Run also needed to be called on flask instead of using the flask cmd line call.
"""

from Flask import base
import multiprocessing
import sys, os, webbrowser

if __name__ == '__main__':
    multiprocessing.freeze_support()

    # not checking for if this is packaged because this script is only used for packaging
    gdalPath = os.path.join(sys._MEIPASS, 'Library', 'share', 'gdal')
    projPath = os.path.join(sys._MEIPASS, 'Library', 'share', 'proj')
    print(gdalPath)
    print(projPath)
    if os.path.isdir(gdalPath):
        os.environ['GDAL_DATA'] = gdalPath
    if os.path.isdir(projPath):
        os.environ['PROJ_LIB'] = projPath
    webbrowser.open('http://localhost:5000')
    base.api.run()
"""
'main' file outside of module to help pyinstaller build an exe and run the flask service

    Builds from inside the module cause issues with relative imports.
    Run also needed to be called on flask instead of using the flask cmd line call.
"""

from Flask import base
import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()
    base.api.run()
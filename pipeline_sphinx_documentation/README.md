# CO2 Pipeline Tool Documentation using Sphinx
Repo for the source Sphinx files and build files for the CO2 Pipeline documentation. 

## Installation
If needed, create a virtual environment for sphinx. The main pipeline virtual environment is seperate from the sphinx one.
Navigate to exported_venv, and execute the following in the anaconda terminal:

    conda env create --name sphinxpipe --file=environment.yml
    
Then activate the virtual environemnt via:

    conda activate sphinxpipe

## Contributing and Building Content
This project uses MyST parser to create new markdown content.

Add to or create markdown files following what is expected by [MyST](https://myst-parser.readthedocs.io/en/latest/index.html) and [Sphinx](https://www.sphinx-doc.org/en/master/).

To build your changes, execute the makefile on unix via `make html`, or `make.bat html` on Windows.

(What worked for me was './make.bat html' via git bash on Windows).


## Looking at the Output Documentation

The built html files in the `_build/html` folder can be viewed with any web browser. The main page that leads to all others is index.html.
I have modified the `_build` folder to be at the same directory level as `source`, instead of the default which is inside of `source`.

## Adding New Documentation to the Actual Tool
The tool will only read documenation that is in the ./public folder. The documentation folder at the root level is just to build documentation. 
To actually add the documentation to the tool, manually copy and paste the new "_build" folder over the old one with the same name in the Flask/public directory

# ML-Integrated Pipeline Webapp
Webapp to generate pipeline route coordinates and corresponding report and shapefile based on user-input start and destination points.

## How To Run As Bundle
Download and run via https://github.com/NETL-RIC/pipeline-routing-tool-release

# Developer Notes

## Download Assets
If you're a member of EDX, pass your EDX API key as an argument to the install_edx_assets.py in the root folder.
This will pull a few assets that are too large to be uploaded to a git repo, from a public EDX workspace, and place them in the right local folder.

    python install_edx_assets.py <edx api key>

## How To Run From Source
In a terminal window, enter `python -m flask run` in ./Flask, with the appropriate virtual environment.
In a different terminal window, enter `npm start` in the root project dir, ensuring that npm and node.js have been installed.

## Backend Dependencies (Flask/Python)
Install the python dependencies to a python virtual env file:

    uv sync --locked
    source ./venv/bin/activate

## Frontend Dependencies (React/JS)
All project dependencies are listed in the package.json. You can install them all by entering

    npm install

in the root project folder where the file is (not in ~/src). If that command yields errors, try adding the following flag to the command:

    npm install --legacy-peer-deps

### Javascript Dependency Errors
If 'module not found, can't resolve: examplepackage' errors occur, try installing the package manually via:

    npm install examplepackage --legacy-peer-deps

## Desktop Packaging
### Flask
The flask server can be bundled with pyInstaller by running `python -m PyInstaller packCO2PRT.spec` which bundles via the *CO2PRT.py* file and dependencies /definitions in the spec file.

Additional dependencies should be picked up automatically by pyinstaller, if they are missed they can be included in the `hiddenimports` list within the spec file.

PyInstaller can be asked to copy necessary data via the `more_datas` list of tuples in the spec file. Format is `('<source location>', '<packaged destination>')`.

If the dev environment doesn't agree with pyinstaller there is a `pyinstaller_env.yml` included that should bundle without issue.

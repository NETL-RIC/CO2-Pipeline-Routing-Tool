# ML-Integrated Pipeline Webapp
Webapp to generate pipeline route coordinates and corresponding report and shapefile based on user-input start and destination points.

## How To Run As Bundle
Download and run via https://github.com/NETL-RIC/pipeline-routing-tool-release

# Developer Notes

## Download Assets
If you're a member of EDX, pass your EDX API key as an argument to the install_edx_assets.py in the root folder.
This will pull a few assets that are too large to be uploaded to a git repo, from a public EDX workspace, and place them in the right local folder.

    python install_edx_assets.py --api-key <edx api key>

## How To Run From Source
In a terminal window, enter `flask --app base.py run` in ./Flask (or `python -m flask run`), with the appropriate virtual environment.
In a different terminal window, enter `npm start` in the root project dir, ensuring that npm and node.js have been installed.

## Backend Dependencies (Flask/Python)
Install the python dependencies to a python virtual env file:

    uv sync --locked
    source ./venv/bin/activate

The command to activate the venv may also be

    source ./venv/Scripts/activate

### .env files
You'll also need to set a flask secret key in an .env file you create in the Flask folder. Generate a key with

    python -c 'import secrets; print(secrets.token_urlsafe(32))'

directly in your shell, and assign the results to a SECRET_KEY variable in the .env file you created.

Note that the .env file is local only, but the .flaskenv file is in source control.
Both are ignored by production, and for developer convinience. 

## Frontend Dependencies (React/JS)
All project dependencies are listed in the package.json. You can install them all by entering

    npm install --legacy-peer-deps

in the root project folder where the file is (not in ~/src).

### Javascript Dependency Errors
If 'module not found, can't resolve: examplepackage' errors occur, try installing the package manually via:

    npm install examplepackage --legacy-peer-deps

## Running Tests
### React.js
To run the frontend tests, run 

    npm test

in the project root dir. The tests file is ~/src/App.test.js

### Flask
To run the backend tests, run

    python -m unittest tests/tect_mc_agent.py -v

in the FLASK directory (~/Flask). The flask tests file is ~/Flask/tests/test_mc_agent.py

## Desktop Packaging
### Flask
The flask server can be bundled with pyInstaller by running `python -m PyInstaller packCO2PRT.spec` which bundles via the *CO2PRT.py* file and dependencies /definitions in the spec file.

Additional dependencies should be picked up automatically by pyinstaller, if they are missed they can be included in the `hiddenimports` list within the spec file.

PyInstaller can be asked to copy necessary data via the `more_datas` list of tuples in the spec file. Format is `('<source location>', '<packaged destination>')`.

If the dev environment doesn't agree with pyinstaller there is a `pyinstaller_env.yml` included that should bundle without issue.

## Containerization

**NOTE:** The binary assets for the application are not downloaded during the build process. The user must download them with the `install_edx_assets.py` script before building the container. This will unpack them to the appropriate directories so the build process can pull them into the container.

### Docker Example

    docker build -t co2 .
    docker run -p 5000:5000 co2

### Build Details

The build process uses two stages. The first stage builds the React frontend and the second stage builds the Python backend. The frontend is built in a container with Node.js and the backend is built in a container with Python. The frontend is copied to the backend container after it is built as static files. The backend is run via gunicorn and both serves the static front end files and the API.

ENV variables are set in the second stage of the build process. The available variables are:

    hosturl: The host URL for the Flask application.
    nthreads: The number of threads for the Flask application.
    port: The port for the Flask application.
    PREFIX_PATH: The prefix path for the Flask application.

These can be overridden by setting the environment variables in the docker run command.

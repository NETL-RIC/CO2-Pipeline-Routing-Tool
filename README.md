# ML-Integrated Pipeline Webapp
Webapp to generate pipeline route coordinates and corresponding report and shapefile based on user-input start and destination points.

# How To Run As Bundle
Download and run via https://github.com/NETL-RIC/pipeline-routing-tool-release

# How to Run via Containerization 

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


# How To Run As Developer via Environment Creation and Asset Download
Clone the repo, which will take 3.03GB space with all assets downloaded.

## Set Up and Run Backend
In the project root directory, run the following commands, replacing <edx api key> with yours, minus the angle brackets:

    uv sync --locked
    source ./venv/bin/activate
    echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')" > .env
    python install_edx_assets.py --api-key <edx api key>

Then start the flask server by cd'ing to the Flask dir and running:

    flask --app base.by run

The setup commands create a virtual environment, activate it, create an .env file with a secret key, and executes a download script to pull necessary binaries from the EDX workspace into the Flask folder.

## Set Up and Run Frontend
In the project root directory, run the following commands:

    npm install --legacy-peer-deps
    npm start

## Dev Notes

You'll need an EDX account to access an EDX API Key necessary for the install_edx_assets script. This can by found on the main page of your edx account after logging in on a browser.

Note that the .env file is local only, but the .flaskenv file is in source control.
Both are ignored by production, and for developer convinience. 


# Running Tests
### React.js
To run the frontend tests, run 

    npm test

in the project root dir. The tests file is ~/src/App.test.js

### Flask
To run the backend tests, run

    python -m unittest tests/tect_mc_agent.py -v

in the FLASK directory (~/Flask). The flask tests file is ~/Flask/tests/test_mc_agent.py

# How to Package as a Desktop Binary (Not Recommended, Legacy Notes for Dev)
### Flask
The flask server can be bundled with pyInstaller by running `python -m PyInstaller packCO2PRT.spec` which bundles via the *CO2PRT.py* file and dependencies /definitions in the spec file.

Additional dependencies should be picked up automatically by pyinstaller, if they are missed they can be included in the `hiddenimports` list within the spec file.

PyInstaller can be asked to copy necessary data via the `more_datas` list of tuples in the spec file. Format is `('<source location>', '<packaged destination>')`.

If the dev environment doesn't agree with pyinstaller there is a `pyinstaller_env.yml` included that should bundle without issue.

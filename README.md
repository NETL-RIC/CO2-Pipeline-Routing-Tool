# ML-Integrated Pipeline Webapp
Flask and React webapp migrated from the original Pipeline PyQT standalone Desktop app.

# Developer Notes
## How To Run
In a terminal window, enter python -m flask run in ./Flask, with the appropriate virtual environment.
In a different terminal window, enter npm start in the root project dir, ensuring that npm and node.js have been installed.

## Dependencies
### Backend Dependencies (Flask)
A working conda virtual environment has been exported to ./exported_vevn/env.yml. Import this into a new conda environment, 
call test() in the main body of ./Flask/base.py, and run base.py from the Flask directory. This script is the entrypoint
for all of the backend logic, and if test() is called successfully then all dependencies are functional. 

Frequently conda will not install all of the libraries listed, so you may have to manually install some of them
via the error messages that appear when running test() in base.py, but between conda and pip you should be able
to 

### Frontend Dependencies (React)
Make sure node.js and npm (node package manager) are installed on your computer. To determine if node.js and npm are installed,
run node -v and npm -v on the command line. If it is properly installed, you should see text that tells you which version
it is. An error or warning will show if it is not installed.

If node.js and npm are not installed on your computer, contact IT to install it for you as it requires admin priviliges. 
Select the Windows installer at https://nodejs.org/en/download. npm comes packaged with node.js, so if node.js is installed,
npm will be installed also. Now retry step 1 to determine if both are installed.

Before running the project, certain library dependencies must be installed for the project to function. These are:

    leaflet
    react-leaflet
    react-widgets
    react-bootstrap
    axios

To install these libraries, open the terminal and enter npm install leaflet, npm install react-leaflet, npm install react-widgets,
npm install react-bootstrap bootstrap, and npm install axios respectively.

## Missing Large Files
Some crucial large files (.tifs) are missing from the repo because they exceed Github's 100MB file size limit without using Github LFS, which
we cannot do. There is a solution for this that uses EDX that is not yet implemented.

## Things To Keep In Mind For Development
When running the flask server, the root project directory from python's point of view will be
ml-pipeline/Flask, not ml-pipeline. Keep this in mind if adding other local packages / modules.
When doing so, try to stick to absolute imports:
    from gym.grid import agent
instead of relative imports
    from .gym.grid import agent

## Directory Structure
The flask folder having few meaningful subdirectories is because of the way the ML Code functions. It was not designed to be ran as a module, 
and therein has some NameError issues whose best fix currently is to keep it in the same directory as the Flask code (base.py being
the entrypoint). This can likely be changed in the future, and may already be able to be changed due to recent fixes, but at time of writing
(03/24) must be kept in one directory due to time constraints.

## Desktop Packaging
### Flask
The flask server can be bundled with pyInstaller by running `python -m PyInstaller packCO2PRT.spec` which bundles via the *CO2PRT.py* file and dependencies /definitions in the spec file.

Additional dependencies should be picked up automatically by pyinstaller, if they are missed they can be included in the `hiddenimports` list within the spec file.

PyInstaller can be asked to copy necessary data via the `more_datas` list of tuples in the spec file. Format is `('<source location>', '<packaged destination>')`.

If the dev environment doesn't agree with pyinstaller there is a `pyinstaller_env.yml` included that should bundle without issue.

### Electron
The electron bundle can be created *after* the flask exe has been packaged by running
`npm run electron:package:win`. This will create an installer file in the `dist` folder
titled `CO2Pipeline setup` which can be distributed to users.

The installer when run will install the app to `/AppData/Local/Programs/apptest/` and
create a shortcut to the electron front end.

#### Potential Electron Building Issues
You may need to manually download electron-builder if `npm run electron:package:win` doesn't automatically install it.
You also may have the incorrect electron-builder package and will get a 7zip permissions error if using the most recent version of the electron-builder package.
Fix either of these problems by installing or downgrading the package respectively, with `npm install electron-builder@24.6.3`. 

You may also get other permissions errors when building, from the WinCodeSign-2.6.0 or nsis-3.0.4.1 packages.
Fix the former by renaming one of the folders inside C:\Users\leveckis\AppData\Local\electron-builder\Cache\winCodeSign\ from a 9-digit string of numbers to `WinCodeSign-2.6.0.` If there are mulitiple of these folders, renaming just one should work.
Fix the nsis error by renaming one of the folders inside C:\Users\yourusername\AppData\Local\electron-builder\Cache\nsis\ from a 9-digit strong of numbers to `nsis-3.0.4.1`


>NOTE: Currently there is a bug with the tool where if the backend is launched by the frontend it will not spawn a shell window and will not be closed when the main window is closed forcing the user to close it with Task Manager. To avoid this the backend must be launched manually for the time being so there is a closeable window. It can be found at `Appdata/Local/Programs/apptest/dist/CO2PRT_Flask.exe`
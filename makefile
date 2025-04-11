# Makefile for building portable flask exe with static react files.
# Required to be run from a terminal with the correct node and python environments

REACT_DIR 				?= ./public
FLASK_DIR 				?= ./Flask
REACT_BUILD_OUTPUT_DIR 	?= ./build
REACT_IN_FLASK_DIR 		?= $(FLASK_DIR)/build
PYINSTALLER_SPEC_FILE 	?= packCO2PRT.spec
PACKAGE_BASENAME 		?= Smart_CO2_Transport
PYINSTALLER_DIST_DIR 	?= ./dist

NPM         = npm
XCOPY       = xcopy
RMDIR       = rmdir /S /Q
DEL         = del /Q
MKDIR       = mkdir
PYI 		= PyInstaller
PY      	= python
POWERSHELL  = powershell -Command

.PHONY: all build_react copy_frontend build_pyinstaller package clean

all: build_pyinstaller

build_react:
	@echo --- Building React Frontend ---
	$(NPM) install && $(NPM) run build
	@echo --- React Frontend Build Complete ---

copy_frontend: build_react
	@echo --- Copying React build to Flask project ---
	-$(RMDIR) "$(FLASK_IN_FLASK_DIR)"
	-$(MKDIR) "$(FLASK_IN_FLASK_DIR)"
	-$(XCOPY) $(REACT_BUILD_OUTPUT_DIR)/* $(FLASK_IN_FLASK_DIR)/ /Y

build_pyinstaller: copy_frontend
	@echo --- Building PyInstaller Bundle ---
	$(PY) -m $(PYI) $(PYINSTALLER_SPEC_FILE) -y
	@echo --- PyInstaller Bundle Build Complete ---

package:
	@echo --- Packaging Application ---
	$(POWERSHELL) "$$timestamp = Get-Date -Format 'MMddyyyy_HHmmss'; $$zipFileName = '$(PACKAGE_BASENAME)_$$timestamp.zip'; Compress-Archive -Path 'dist\$(PACKAGE_BASENAME)' -DestinationPath $$zipFileName;"
	@echo --- Packaging Complete ---

clean:
	@echo --- Cleaning Project ---
	-$(RMDIR) "$(REACT_IN_FLASK_DIR)"
	-$(RMDIR) "$(REACT_BUILD_OUTPUT_DIR)"
	-$(RMDIR) "$(PYINSTALLER_DIST_DIR)"

check_ps:
	POWERSHELL $env:PROCESSOR
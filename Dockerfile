# Stage 1: Build React Frontend, let this happen in the container build process
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy package.json and package-lock.json
COPY public/package.json ./
COPY public/package-lock.json ./

# Install npm dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the frontend source code
COPY public/ ./

# Build the React application
RUN npm run build

# Stage 2: Python Runtime Environment
FROM python:3.10-slim AS runtime

WORKDIR /app

# Install system dependencies required by GDAL
# This list might need adjustment...
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    proj-bin \
    libproj-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL/PROJ data
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

# Install uv, could use Conda but conda commands are a pain in containers, and uv has a workaround for GDAL
RUN pip install uv

# Copy pyproject.toml to install dependencies
# COPY pyproject.toml ./

# Copy uv.lock to install dependencies
# Ideally this is a better solution because it uses exact resolved versions that we know
#  will work. If this doesn't work within the container we can fall back on the pyproject.toml
COPY uv.lock ./

# Install Python dependencies using uv
RUN uv sync --locked

# Copy the Flask backend code
COPY Flask/ ./Flask/

# Copy the built React frontend from the builder stage to where Flask expects it
COPY --from=frontend-builder /app/frontend/build ./Flask/build/

# Ensure these paths are relative to the Dockerfile context
COPY Flask/cost_surfaces ./Flask/cost_surfaces/
COPY Flask/raster ./Flask/raster/
COPY Flask/other_assets ./Flask/other_assets/
COPY Flask/report_builder/inputs ./Flask/report_builder/inputs/
COPY Flask/report_builder/images ./Flask/report_builder/images/
COPY public/documentation ./Flask/build/documentation/

# Expose the port Flask will run on
EXPOSE 5000

# Command to run the Flask application
# This is mirroring how we run the flask app in CO2PRT.py which is the pyinstaller main entry point
# Using host='0.0.0.0' makes the server accessible from outside the container.
# We will need to use a production server down the road. Testing with flasks development server is OK for now
CMD ["uv", "run", "python", "-c", "from Flask import base; base.api.run(host='0.0.0.0', port=5000)"]
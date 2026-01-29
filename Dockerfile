# Stage 1: Build React Frontend, let this happen in the container build process
FROM node:20-slim AS frontend-builder

WORKDIR /app

# Copy package.json and package-lock.json
COPY ./package.json .
COPY ./package-lock.json .

# Install npm dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the frontend source code
COPY src/ ./src/
COPY public/ ./public/

# Build the React application
RUN npm run build

# Stage 2: Python Runtime Environment
FROM python:3.10-slim AS runtime

ENV hosturl="0.0.0.0"
ENV nthreads=10
ENV port=5000
ENV PREFIX_PATH="/co2-pipeline-routing-tool/"

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

 # Install requirements for opencv-python
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Set environment variables for GDAL/PROJ data
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

# Install uv, could use Conda but conda commands are a pain in containers, and uv has a workaround for GDAL
RUN pip install uv

# Copy uv.lock to install dependencies
# Ideally this is a better solution because it uses exact resolved versions that we know
#  will work. If this doesn't work within the container we can fall back on the pyproject.toml
COPY uv.lock ./
COPY pyproject.toml ./

# Install Python dependencies using uv
RUN uv sync
# RUN uv add waitress
RUN uv add gunicorn tqdm

# Copy the Flask backend code
COPY Flask/ ./Flask/

# Copy the built React frontend from the builder stage to where Flask expects it
COPY --from=frontend-builder /app/build ./build/

# Ensure these paths are relative to the Dockerfile context
# COPY Flask/cost_surfaces ./Flask/cost_surfaces/
# COPY Flask/raster ./Flask/raster/
# COPY Flask/report_builder/inputs ./Flask/report_builder/inputs/
# COPY Flask/report_builder/images ./Flask/report_builder/images/
COPY public/documentation ./Flask/build/documentation/

# Expose the port Flask will run on
EXPOSE ${port}

# Command to run the Flask application
CMD ["sh", "-c", "exec uv run gunicorn --bind=${hosturl}:${port} --workers=${nthreads} Flask.base:api"] 
# Alternate to uv run is to activate the environment:
# ENV PATH="/app/.venv/bin:$PATH"

# https://docs.astral.sh/uv/guides/integration/docker/
# Need to look into using the distroless docker images to copy uv binaries.

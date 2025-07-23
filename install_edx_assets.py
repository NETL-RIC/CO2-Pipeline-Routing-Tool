""" Pass EDX API key as 'apikey' argument in CLI to pull down files stored on the EDX Workspace.
Example:
    python install_edx_assets.py xxxx-xxxxx-xxxxx-xxxxx
Downloads:
    Flask/report_builder/inputs/tract_base.shp
    Flask/report_buidler/inputs/data_by_10km_grid.csv
Reference: https://edx.netl.doe.gov/sites/edxapidocs/downloadResourceFiles.html
"""
import requests
import argparse
import os

parser = argparse.ArgumentParser(description="Script to download files to local with EDX API Key")
parser.add_argument('apikey', help='Your personal edx api key connected to your edx account')
args = parser.parse_args()

DOWNLOAD_FOLDER='./Flask/report_builder/inputs/'

# The file id's for the edx files we want to download. From resource details
file_ids = ['005768b9-0809-403a-a3e6-5860d4ee09a0','756a1ea7-4057-46dc-b657-8729be0f478f']

for file_id in file_ids:
    headers = {
        "EDX-API-Key": args.apikey,
        "User-Agent": 'EDX-USER',
    }

    params = {
        'resource_id': file_id,
    }

    url = 'https://edx.netl.doe.gov/api/3/resource_download'

    # Get filename from headers
    print("Sending request to resource data...")
    response_head = requests.head(url, headers=headers, params=params)
    if response_head.status_code != 200:
        print(f"Failed to get resource data. Status code: {response_head.status_code}")
        exit(1)

    content_disposition = response_head.headers.get('Content-Disposition')

    # Set the filename from the Content-Disposition header if available
    filename = None
    if content_disposition and 'filename=' in content_disposition:
        filename = content_disposition.split('filename=')[-1].strip('"')

    # Get the content length from headers and determine resource size.
    content_length = response_head.headers.get('Content-Length')
    resource_size = int(content_length) if content_length is not None else None

    print("Resource Name:", filename)
    print(f"Resource Size: {resource_size} bytes")

    # Determine if partial file exists
    existing_size = 0
    if os.path.exists(filename):
        existing_size = os.path.getsize(filename)
        print(f"File already exists. The current file size is: {existing_size} bytes.")

        if resource_size is not None:
            print(f"Resource file size: {resource_size} bytes")
            if existing_size >= resource_size:
                print("File already fully downloaded in current directory.")
                exit(0)

        headers['Range'] = f'bytes={existing_size}-'
        print(f"Resuming download from byte: {existing_size}")
    else:
        print(f"Starting download for: {filename}")

    # Begin download stream
    print(headers, url)
    response = requests.get(url, headers=headers, params=params, stream=True)

    print(f"Download response status code: {response.status_code}")
    if response.status_code in (200, 206):
        # If the server returns a 206 (for partial content), use 'ab' mode to append
        mode = 'ab' if response.status_code == 206 else 'wb'
        total_bytes = existing_size
        dl_target = os.path.abspath(DOWNLOAD_FOLDER + filename)
        print(f"Saving to: {dl_target}")
        print('dl_target: ' + dl_target)
        with open(dl_target, mode) as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_bytes += len(chunk)
                    if resource_size:
                        percent = (total_bytes / resource_size) * 100
                        print(f"\rDownloaded: {total_bytes} bytes ({percent:.2f}%)", end='', flush=True)
                    else:
                        # If resource size is unknown, just show bytes downloaded
                        print(f"\rDownloaded: {total_bytes} bytes", end='', flush=True)

        print(f"\nDownload complete.")
        print(f"Total bytes downloaded: {total_bytes}")
    else:
        print(f"Download Failed. Status code: {response.status_code}")
        try:
            print("Response:", response.json())
        except Exception:
            print("Non-JSON response:", response.text)
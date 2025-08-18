import os
import re
import shutil
import urllib.request
from zipfile import ZipFile
from wheel.cli.unpack import unpack
from wheel.cli.pack import pack

gdal_wheel_url = "https://github.com/cgohlke/geospatial-wheels/releases/download/v2025.7.4/gdal-3.11.1-cp312-cp312-win_amd64.whl"
fiona_wheel_url = "https://github.com/cgohlke/geospatial-wheels/releases/download/v2025.7.4/fiona-1.10.1-cp312-cp312-win_amd64.whl"
rasterio_wheel_url = "https://github.com/cgohlke/geospatial-wheels/releases/download/v2025.7.4/rasterio-1.4.3-cp312-cp312-win_amd64.whl"

def main():
    # Fiona and rasterio are easy, just download the wheels
    print("Downloading Fiona wheel...")
    urllib.request.urlretrieve(fiona_wheel_url, fiona_wheel_url.split('/')[-1])
    print("...Complete. Downloading rasterio wheel...")
    urllib.request.urlretrieve(rasterio_wheel_url, rasterio_wheel_url.split('/')[-1])
    print("...Complete. Downloading GDAL wheel...")

    # Download the Windows GDAL wheel (Unfortunately, it does not include required include headers)
    gdal_wheel = gdal_wheel_url.split('/')[-1]
    gdal_version = re.search(r"gdal-([\d.]+)", gdal_wheel_url).group(1)
    urllib.request.urlretrieve(gdal_wheel_url, gdal_wheel)
    print("...Complete.")

    # Unpack the wheel into a directory
    gdal_wheel_dir = f"gdal-{gdal_version}"
    unpack(gdal_wheel)
    os.remove(gdal_wheel)

    # Read the names of include files we need to add to the whl
    include_filenames = []
    with open("gdal_includes.txt", "r") as f:
        include_filenames = f.read().splitlines()

    # Download the GDAL source
    print("Downloading GDAL source...")
    gdal_src_url = f"https://github.com/OSGeo/gdal/archive/refs/tags/v{gdal_version}.zip"
    gdal_src_zip = gdal_src_url.split('/')[-1]
    urllib.request.urlretrieve(gdal_src_url, gdal_src_zip)
    print("...Complete.")

    # Add the include files into the wheel directory
    with ZipFile(gdal_src_zip, 'r') as zip:
        file_list = zip.namelist()
        for filename in file_list:
            if filename.split("/")[-1] in include_filenames:
                zip.extract(filename, os.path.join(gdal_wheel_dir, "osgeo", "include", "gdal", filename.split("/")[-1]))

    os.remove(gdal_src_zip)

    # Repackage the wheel
    pack(gdal_wheel_dir, dest_dir=".", build_number=None)
    shutil.rmtree(gdal_wheel_dir)


if __name__ == "__main__":
    main()
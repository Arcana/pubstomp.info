from .. import app
from ..geo.models import Geoname
import zipfile
import requests
import sys
import os

LATEST_DATA_URL = app.config['GEODATA_URL']
DATA_FILE = app.config['GEODATA_FILE']
TMP_ZIP = app.config['GEODATA_TMP_ZIP']
TMP_EXTRACT = app.config['GEODATA_TMP_EXTRACT']


def update_geonames():
    print("Getting latest data")
    with open(TMP_ZIP, 'wb') as f:
        req = requests.get(LATEST_DATA_URL)
        if not req.ok:
            print("Not got data notwoop!")
            sys.exit()

        print("Got data woop!")
        for block in req.iter_content(1024):
            f.write(block)

    if not zipfile.is_zipfile(TMP_ZIP):
        print("No zipfile notwoop!")
        sys.exit()

    print("Got zipfile woop!")
    zip_data = zipfile.ZipFile(TMP_ZIP)
    if DATA_FILE in zip_data.namelist():
        print("Data in zipfile woop!")
        zip_data.extract(DATA_FILE, TMP_EXTRACT)
    else:
        print("Data not in zipfile notwoop!")

    print("Import data woop!")
    Geoname.import_from_tsv(os.path.join(TMP_EXTRACT, DATA_FILE))


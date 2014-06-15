from .. import app
from ..geo.models import Geoname
import zipfile
import requests
import sys
import os


def update_country(country_code):
    latest_data_url = app.config['GEODATA_URL'].format(country_code)
    data_file = app.config['GEODATA_FILE'].format(country_code)
    tmp_zip = app.config['GEODATA_TMP_ZIP'].format(country_code)
    tmp_extract = app.config['GEODATA_TMP_EXTRACT'].format(country_code)

    print("Getting latest data")
    with open(tmp_zip, 'wb') as f:
        req = requests.get(latest_data_url)
        if not req.ok:
            print("Not got data notwoop!")
            sys.exit()

        print("Got data woop!")
        for block in req.iter_content(1024):
            f.write(block)

    if not zipfile.is_zipfile(tmp_zip):
        print("No zipfile notwoop!")
        sys.exit()

    print("Got zipfile woop!")
    zip_data = zipfile.ZipFile(tmp_zip)
    if data_file in zip_data.namelist():
        print("Data in zipfile woop!")
        zip_data.extract(data_file, tmp_extract)
    else:
        print("Data not in zipfile notwoop!")

    print("Import data woop!")
    Geoname.import_from_tsv(os.path.join(tmp_extract, data_file))


def update_geonames():
    for country_code in app.config['GEODATA_COUNTRIES']:
        print("Getting data for {}").format(country_code)
        update_country(country_code)


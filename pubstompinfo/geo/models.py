"""
Models for Geonames.org exported data
http://download.geonames.org/export/dump/readme.txt
"""

from .. import db
import os
import csv
from ..helpers import grouper
from MySQLdb import escape_string


class Geoname(db.Model):
    """ Represents features, e.g. cities, lakes, parishes, counties... like 50 different things
    """
    # Columns
    geonameid = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Will get from data source
    name = db.Column(db.String(200), index=True)         # Name
    asciiname = db.Column(db.String(200))                # Ascii name
    alternatenames = db.Column(db.String(8000))          # CSV
    latitude = db.Column(db.Float(10, 6))                # wgs84
    longitude = db.Column(db.Float(10, 6))               # wgs84
    feature_class = db.Column(db.String(1), index=True)  # see http://www.geonames.org/export/codes.html
    feature_code = db.Column(db.String(10), index=True)  # see http://www.geonames.org/export/codes.html
    country_code = db.Column(db.String(2), index=True)   # Country code
    cc2 = db.Column(db.String(60))                       # alternate country codes, comma separated, ISO-3166 2-letter country
                                                         # code
    admin1_code = db.Column(db.String(20))               # fipscode (subject to change to iso code), see exceptions below, see
                                                         # file admin1Codes.txt for display names of this code
    admin2_code = db.Column(db.String(80))               # code for the second administrative division, a county in the US, see
                                                         # file admin2Codes.txt
    admin3_code = db.Column(db.String(20))               # code for third level administrative division
    admin4_code = db.Column(db.String(20))               # code for fourth level administrative division
    population = db.Column(db.BigInteger, index=True)    # Population
    elevation = db.Column(db.Integer)                    # Meters
    dem = db.Column(db.Integer)                          # digital elevation model, srtm3 or gtopo30, average elevation of
                                                         # 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters,
                                                         # integer. srtm processed by cgiar/ciat. (wot)
    timezone = db.Column(db.String(40))                  # the timezone id (see file timeZone.txt)
    modification_date = db.Column(db.Date)               # Last updated date

    # Set default order by
    __mapper_args__ = {
        "order_by": [db.desc(population)]
    }

    # Use MyISAM to become a race car
    __table_args__ = {'mysql_engine': 'MyISAM'}

    # Static data
    CITY_CLASS = 'P'       # settlements
    COUNTRY_CLASS = 'A'    # country, state, region,...
    COUNTRY_CODE = 'PCLI'  # independent political entity

    def __init__(self, geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, feature_code,
                 country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code,
                 population, elevation, dem, timezone, modification_date):
        self.geonameid = geonameid
        self.name = name
        self.asciiname = asciiname
        self.alternatenames = alternatenames
        self.latitude = latitude
        self.longitude = longitude
        self.feature_class = feature_class
        self.feature_code = feature_code
        self.country_code = country_code
        self.cc2 = cc2
        self.admin1_code = admin1_code
        self.admin2_code = admin2_code
        self.admin3_code = admin3_code
        self.admin4_code = admin4_code
        self.population = population
        self.elevation = elevation
        self.dem = dem
        self.timezone = timezone
        self.modification_date = modification_date

    @classmethod
    def get_cities(cls):
        return cls.query.filter(cls.feature_class == cls.CITY_CLASS)

    @classmethod
    def get_countries(cls):
        return cls.query.filter(cls.feature_class == cls.COUNTRY_CLASS, cls.feature_code == cls.COUNTRY_CODE)

    @classmethod
    def import_from_tsv(cls, filepath):
        if not os.path.exists(filepath):
            return False

        with open(filepath, 'rb') as tsv_file:
            tsv_data = csv.reader(tsv_file, delimiter='\t', quoting=csv.QUOTE_NONE)

            i = 0
            CHUNK_SIZE = 1024
            for chunk in grouper(tsv_data, CHUNK_SIZE):
                print("Importing {} to {}".format(i, i+CHUNK_SIZE))

                # Filter chunk, we only want cities and countries.
                filtered_chunk = []
                for row in chunk:
                    if row is not None and (row[6] == cls.CITY_CLASS or (row[6] == cls.COUNTRY_CLASS and row[7] == cls.COUNTRY_CODE)):
                        filtered_chunk.append(row)

                if not len(filtered_chunk):
                    continue

                keys = [
                    'geonameid',
                    'name',
                    'asciiname',
                    'alternatenames',
                    'latitude',
                    'longitude',
                    'feature_class',
                    'feature_code',
                    'country_code',
                    'cc2',
                    'admin1_code',
                    'admin2_code',
                    'admin3_code',
                    'admin4_code',
                    'population',
                    'elevation',
                    'dem',
                    'timezone',
                    'modification_date'
                ]

                # Esacping %'s because MySQLdb is tries to format the string using the old string format, and errors if the data contains %.
                query = "REPLACE INTO geoname ({}) VALUES ({})".format(
                    ",".join(keys),
                    "), (".join(["'{}'".format("', '".join([escape_string(x.replace('%', '%%')) for x in row])) for row in filtered_chunk])
                )

                db.engine.execute(query)
                i += CHUNK_SIZE

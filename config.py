import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
TESTING = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

CACHE_MEMCACHED = {
    'CACHE_TYPE': "memcached",
    'CACHE_MEMCACHED_SERVERS': ["127.0.0.1:11211"],
    'CACHE_KEY_PREFIX': "pubstomp-info"
}

CACHE_FS = {
    'CACHE_TYPE': "filesystem",
    'CACHE_DIR': APP_DIR + os.sep + '.cache'
}

# Timeouts
UPDATE_LEAGUES_TIMEOUT = 60 * 60 * 6  # 6 hours
UPDATE_USER_NAME_TIMEOUT = 60 * 60  # 1 hour


# General vars
SITE_NAME = "Pubstomp.info"
SITE_DESCRIPTION = "A directory for Dota 2 pubstomps across the world."
GITHUB_URL = "http://github.com/Arcana/pubstomp.info"
ISSUE_TRACKER_URL = "http://github.com/Arcana/pubstomp.info/issues"
CONTACT_EMAIL = "gief@arcana.io"
DATE_STRING_FORMAT = "%d %b %Y, %H:%M"
USERS_PER_PAGE = 32
LEAGUES_PER_PAGE = 12
COUNTRIES_PER_PAGE = 64
CITIES_PER_PAGE = 64
EVENTS_PER_PAGE = 12
SHORT_DESCRIPTION_LENGTH = 140

# Geodata
GEODATA_COUNTRIES = ['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AW', 'AX', 'AZ',
                     'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS',
                     'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CC', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN',
                     'CO', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE',
                     'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF',
                     'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM',
                     'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM',
                     'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC',
                     'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK',
                     'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA',
                     'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG',
                     'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS', 'PT', 'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW',
                     'SA', 'SB', 'SC', 'SD', 'SE', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS',
                     'ST', 'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO',
                     'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'UM', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI',
                     'VN', 'VU', 'WF', 'WS', 'XK', 'YE', 'YT', 'ZA', 'ZM', 'ZW']  # List of country codes to import
GEODATA_URL = "http://download.geonames.org/export/dump/{}.zip"
GEODATA_FILE = "{}.txt"
GEODATA_TMP_ZIP = "/tmp/pubstomp_geodata_{}.zip"
GEODATA_TMP_EXTRACT = "/tmp/pubstomp_geodata_{}"

# NSA
GA_TRACKING_SNIPPET = """
<script>
    <!-- Google Analytics -->
</script>
"""

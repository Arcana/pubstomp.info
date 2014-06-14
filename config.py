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
SITE_DESCRIPTION = "A directory for Dota 2 pubstomps across the world, for a variety of leagues."
GITHUB_URL = "http://github.com/Arcana/pubstomp.info"
ISSUE_TRACKER_URL = "http://github.com/Arcana/pubstomp.info/issues"
CONTACT_EMAIL = "gief@arcana.io"
DATE_STRING_FORMAT = "%d %b %Y, %H:%M"
USERS_PER_PAGE = 32
LEAGUES_PER_PAGE = 12

# NSA
GA_TRACKING_SNIPPET = """
<script>
    <!-- Google Analytics -->
</script>
"""

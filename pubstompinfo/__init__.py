# New Relic agent
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

# Muh imports
from flask import Flask
from flask.ext.cache import Cache
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.markdown import Markdown
from raven.contrib.flask import Sentry
import steam
import os

# Create app
app = Flask(__name__,
            instance_relative_config=True,
            instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance/'))

# Load default config
app.config.from_object("config")

# Load instance config
app.config.from_pyfile("config.py")

# Load extensions
mem_cache = Cache(app, config=app.config["CACHE_MEMCACHED"])
fs_cache = Cache(app, config=app.config["CACHE_FS"])
db = SQLAlchemy(app)
login_manager = LoginManager(app)
oid = OpenID(app)
markdown = Markdown(app, safe_mode="escape")
sentry = Sentry(app)

# Setup steamodd
steam.api.key.set(app.config['STEAM_API_KEY'])
steam.api.socket_timeout.set(5)

# Setup debugtoolbar if we're in debug mode.
if app.debug:
    from flask.ext.debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)


# Set up jinja2 filters.
from .filters import escape_every_character,\
    timestamp_to_datestring,\
    datetime_to_datestring,\
    seconds_to_time,\
    number_format
app.add_template_filter(escape_every_character)
app.add_template_filter(timestamp_to_datestring)
app.add_template_filter(datetime_to_datestring)
app.add_template_filter(seconds_to_time)
app.add_template_filter(number_format)


# Load current app version into globals
from .helpers import current_version
app.config['VERSION'] = current_version()

# Load views
import views

# Load blueprints
from .users.views import mod as users_module
app.register_blueprint(users_module)

from .leagues.views import mod as leagues_module
app.register_blueprint(leagues_module)

from .geo.views import mod as geo_module
app.register_blueprint(geo_module)

from .events.views import mod as event_module
app.register_blueprint(event_module)

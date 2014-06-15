from flask import Blueprint, render_template, current_app
from models import Geoname


mod = Blueprint("geo", __name__, url_prefix="/geo")


@mod.route("/countries")
@mod.route("/countries/page/<int:page>/")
def countries(page=1):
    _countries = Geoname.get_countries().paginate(page, current_app.config['COUNTRIES_PER_PAGE'])

    return render_template("geo/countries.html",
                           title="Countries - {}".format(current_app.config['SITE_NAME']),
                           countries=_countries)


@mod.route("/cities")
@mod.route("/cities/page/<int:page>/")
def cities(page=1):
    _cities = Geoname.get_cities().paginate(page, current_app.config['CITIES_PER_PAGE'])

    return render_template("geo/cities.html",
                           title="Cities - {}".format(current_app.config['SITE_NAME']),
                           cities=_cities)

from flask import Blueprint, render_template, current_app, abort, jsonify
from models import Geoname
from ..events.models import Event
from .. import db

import json

mod = Blueprint("geo", __name__, url_prefix="/geo")


@mod.route("/countries/")
@mod.route("/countries/page/<int:page>/")
def countries(page=1):
    _countries = Geoname.get_countries().paginate(page, current_app.config['COUNTRIES_PER_PAGE'])

    return render_template("geo/countries.html",
                           title="Countries - {}".format(current_app.config['SITE_NAME']),
                           countries=_countries)


@mod.route("/cities/")
@mod.route("/cities/page/<int:page>/")
def cities(page=1):
    _cities = Geoname.get_cities(). \
        join(Event). \
        group_by(Geoname.geonameid). \
        order_by(db.func.count(Event.id).desc()
    ).paginate(page, current_app.config['CITIES_PER_PAGE'])

    # Get counts for this page of cities (fuck knows how to include it with the above call ^)
    counts = dict(db.session.query(Event.city_id, db.func.count(Event.id)).group_by(Event.city_id).filter(
        Event.city_id.in_([city.geonameid for city in _cities.items])).all())

    for item in _cities.items:
        item.events_count = counts.get(item.geonameid) or 0

    return render_template("geo/cities.html",
                           title="Cities - {}".format(current_app.config['SITE_NAME']),
                           cities=_cities)


@mod.route("/cities/<int:_id>")
def city(_id):
    _city = Geoname.query.filter(Geoname.geonameid == _id).first_or_404()

    return render_template("geo/city.html",
                           title=u"{} - {}".format(_city.name, current_app.config['SITE_NAME']),
                           city=_city)


@mod.route("/cities/autocomplete/<string:query>.json")
def city_autocomplete(query=None):
    if "," in query:
        query, delim, cc = query.partition(",")
        data = Geoname.city_autocomplete(query.strip(), cc=cc.strip())
    else:
        data = Geoname.city_autocomplete(query)

    return json.dumps([{
        "value": item.geonameid,
        "name": unicode(item)
    } for item in data])

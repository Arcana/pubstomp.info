from flask import render_template, flash
from . import app, db
from flask.ext.login import current_user
from events.models import Event, EventDay
from geo.models import Geoname
from leagues.models import League
from datetime import datetime


# Routes
@app.route('/')
def index():
    """
    Pubstomp.info home page. TODO
    :return: Response
    """

    events = Event.query.filter(Event.days.any(EventDay.end_time > datetime.now()))
    new_events = events.order_by(Event.created_at).limit(8)

    popular_leagues = League.query.join(Event).\
        filter(Event.days.any(EventDay.end_time > datetime.now())).\
        limit(4). \
        all()

    popular_cities = Geoname.get_cities(). \
        join(Event). \
        filter(
            Event.days.any(EventDay.end_time > datetime.now())). \
            group_by(Geoname.geonameid). \
            order_by(db.func.count(Event.id).desc()
        ). \
        limit(8). \
        all()

    # Get counts for this page of cities (fuck knows how to include it with the above call ^)
    city_counts = dict(db.session.query(Event.city_id, db.func.count(Event.id)).group_by(Event.city_id).filter(
        Event.city_id.in_([city.geonameid for city in popular_cities])).all())

    for item in popular_cities:
        item.events_count = city_counts.get(item.geonameid) or 0

    return render_template("index.html",
                           events=events,
                           new_events=new_events,
                           popular_cities=popular_cities,
                           popular_leagues=popular_leagues)


@app.route('/about')
def about():
    return render_template("about.html",
                           title="About us")


@app.route('/contact')
def contact():
    return render_template("contact.html",
                           title="Contact us")


@app.route('/flash')
def _flash():
    flash("Abcdefghijklmnopqrstuvwxyz", "error")
    flash("Abcdefghijklmnopqrstuvwxyz", "notice")
    flash("Abcdefghijklmnopqrstuvwxyz", "success")

    return render_template("error.html", error=None)


@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # > Missing middle!
@app.errorhandler(500)  # Internal server error.
# @app.errorhandler(Exception)  # Internal server error.
def internalerror(error):
    """ Custom error page, will catch 401, 403, 404, and 500, and output a friendly error message. """
    try:
        if error.code == 401:
            error.description = "I'm sorry Dave, I'm afraid I can't do that.  Try logging in."
        elif error.code == 403:
            if current_user.is_authenticated():
                error.description = "I'm sorry {}, I'm afraid I can't do that.  You do not have access to this resource.".format(current_user.name)
            else:
                # Shouldn't output 403 unless the user is logged in.
                error.description = "Hacker."
    except AttributeError:
        # Rollback the session
        db.session.rollback()

        # E500's don't populate the error object, so we do that here.
        error.code = 500
        error.name = "Internal Server Error"
        error.description = "Whoops! Something went wrong server-side.  Details of the problem has been sent to our developers for investigation."

    # Render the custom error page.
    return render_template("error.html", error=error, title=error.name), error.code

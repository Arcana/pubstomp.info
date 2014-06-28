from flask import Blueprint, render_template, current_app, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from .. import mem_cache, sentry, db
from models import Event, EventVenue, EventDay
from forms import EventForm
from datetime import datetime

mod = Blueprint("events", __name__, url_prefix="/events")


@mod.route("/")
@mod.route("/page/<int:page>/")
def events(page=1):
    _events = Event.query.\
        filter(Event.days.any(EventDay.end_time > datetime.now())).\
        paginate(page, current_app.config['EVENTS_PER_PAGE'])

    return render_template("events/events.html",
                           title="Events - {}".format(current_app.config['SITE_NAME']),
                           events=_events)


@mod.route("/<int:_id>/")
def event(_id):
    _event = Event.query.filter(Event.id == _id).first_or_404()
    return render_template("events/event.html",
                           title="{} - {}".format(_event.name, current_app.config['SITE_NAME']),
                           event=_event)


@mod.route('/create/', methods=["GET", "POST"])
@mod.route('/<int:_id>/edit/', methods=["GET", "POST"])
@login_required
def edit(_id=None):
    _event = Event.query.filter(Event.id == _id).first()
    if _event is not None:
        # Check if current user is an event organiser, if not they can't edit the event.
        if _event.can_edit(current_user) is False:
            abort(403)
    else:
        # We're making a new event
        _event = Event()
        _event.organisers.append(current_user)

    event_form = EventForm(obj=_event)

    if event_form.validate_on_submit():
        _event.league_id = event_form.league.data.id
        _event.city_id = event_form.city.data.geonameid
        _event.name = event_form.name.data
        _event.description = event_form.description.data
        _event.website = event_form.website.data
        db.session.add(_event)
        db.session.flush()

        # Venue
        venue = _event.venue
        if venue is None:
            venue = EventVenue()

        venue.event_id = _event.id
        venue.name = event_form.venue.display_name.data
        venue.address1 = event_form.venue.address1.data
        venue.address2 = event_form.venue.address2.data
        venue.zip_code = event_form.venue.zip_code.data
        venue.capacity = event_form.venue.capacity.data

        if venue.name:
            # Save the venue if it has a name
            db.session.add(venue)
        elif venue.id is not None:
            # It if doesn't have a name and it exists already, delete it's entry.
            db.session.delete(venue)

        # Delete all existing days
        for day in _event.days:
            db.session.delete(day)

        # Create new days from form data
        for _day in event_form.days:
            if _day.start_time.data and _day.end_time.data:
                day = EventDay(
                    _event.id,
                    _day.start_time.data,
                    _day.end_time.data,
                )
                db.session.add(day)

        db.session.commit()

        flash("Event saved", "success")
        return redirect(url_for("events.event", _id=_event.id))

    if _event.id is None:
        title = "Register event - {}".format(current_app.config['SITE_NAME'])
    else:
        title = "Edit {} - {}".format(_event.name, current_app.config['SITE_NAME'])

    return render_template("events/edit.html",
                           title=title,
                           form=event_form,
                           event=_event)

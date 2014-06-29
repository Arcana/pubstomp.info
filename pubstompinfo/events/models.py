from .. import db
from sqlalchemy.ext.hybrid import hybrid_property
import datetime


event_organisers = db.Table("event_organiser",
                            db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                            db.Column('user_id', db.Integer, db.ForeignKey('users.id')))


class Event(db.Model):
    """ Represents a pubstomp event.  Model used to store the various event-related meta-data. """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    city_id = db.Column(db.Integer, db.ForeignKey("geoname.geonameid"))
    league_id = db.Column(db.Integer, db.ForeignKey("league.id"))

    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text())
    website = db.Column(db.String(128))

    # Relationships
    days = db.relationship('EventDay', backref='event', lazy="joined", order_by="EventDay.start_time")
    organisers = db.relationship('User', secondary=event_organisers, backref=db.backref('events', lazy="dynamic"),
                                 lazy="joined")

    venue = db.relationship('EventVenue', backref='event', lazy="joined", uselist=False)

    def __init__(self, city_id=None, league_id=None, name=None, description=None, website=None):
        self.city_id = city_id
        self.league_id = league_id
        self.name = name
        self.description = description
        self.website = website

    def __repr__(self):
        return self.name or ""

    def can_edit(self, user):
        """ Checks whether the given user is allowed to edit this event.
        :param user: User
        :return: bool
        """
        return user in self.organisers or user.is_admin()

    @hybrid_property
    def start_time(self):
        day = EventDay.query.filter(EventDay.event_id == self.id).order_by(EventDay.start_time.asc()).first()
        if day:
            return day.start_time
        return None

    @hybrid_property
    def end_time(self):
        day = EventDay.query.filter(EventDay.event_id == self.id).order_by(EventDay.end_time.desc()).first()
        if day:
            return day.end_time
        return None


class EventDay(db.Model):
    """ Represents a day at an event, as events may last many days with start and end times differing per-day. """

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    # Set default order by
    __mapper_args__ = {
        "order_by": [db.asc(start_time)]
    }

    def __init__(self, event_id=None, start_time=None, end_time=None):
        self.event_id = event_id
        self.start_time = start_time
        self.end_time = end_time


class EventVenue(db.Model):
    """ Represents a venue for an event. """

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))

    name = db.Column(db.String(64), nullable=False)
    address1 = db.Column(db.String(64), nullable=False)
    address2 = db.Column(db.String(64))
    zip_code = db.Column(db.String(64))  # Probably doesn't need to be 64 chars, but who gives a fuck
    # Rest of address will be served by event.city

    capacity = db.Column(db.Integer)

    latitude = db.Column(db.Float(10, 6))
    longitude = db.Column(db.Float(10, 6))

    concessions = None  # TODO
    facilities = None  # TODO

    def __init__(self, event_id=None, name=None, address1=None, address2=None, kappacity=None, latitude=None, longitude=None):
        self.event_id = event_id
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.capacity = kappacity
        self.latitude = latitude
        self.longitude = longitude


    @property
    def display_name(self):
        """ Proxy for self.name, because WTForms doesn't like "name" in a formfield - so we're using display_name there. """
        return self.name

    @display_name.setter
    def display_name(self, value):
        """ Proxy for self.name, because WTForms doesn't like "name" in a formfield - so we're using display_name there. """
        self.name = value

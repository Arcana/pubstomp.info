from flask.ext.wtf import Form
from wtforms import TextField, IntegerField, FormField, FieldList, DateTimeField, DecimalField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Length, URL, Optional, ValidationError
from ..forms import AutocompleteField

from ..geo.models import Geoname
from ..leagues.models import League


def all_cities():
    return Geoname.get_cities().order_by(Geoname.country_code, Geoname.name)


def all_leagues():
    return League.query.order_by(League.name)


class VenueForm(Form):
    display_name = TextField("Name", validators=[Required(), Length(max=64)])
    address1 = TextField("Address 1", validators=[Required(), Length(max=64)])
    address2 = TextField("Address 2", validators=[Optional(), Length(max=64)])
    zip_code = TextField("Zip Code", validators=[Optional(), Length(max=64)])
    capacity = IntegerField("Capacity", validators=[Optional()])

    latitude = DecimalField("Latitude", places=8, validators=[Optional()])
    longitude = DecimalField("Longitude", places=8, validators=[Optional()])

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(VenueForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)


class DayForm(Form):
    start_time = DateTimeField("Opening date & time", validators=[Optional()])
    end_time = DateTimeField("Closing date & time", validators=[Optional()])

    def validate_end_time(self, field):
        if self.start_time.data > field.data:
            raise ValidationError('Closing time must be after opening time.')

    def validate_start_time(self, field):
        if self.end_time.data <= field.data:
            raise ValidationError('Opening time must be before closing time.')

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(DayForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)


class EventForm(Form):
    """ Form to edit an event """
    # Event model data
    league = QuerySelectField("League",
                              validators=[Required()],
                              description="Which league is this pubstomp gathering to watch?",
                              query_factory=all_leagues)

    # city = QuerySelectField("City",
    # validators=[Required()],
    #                         description="In which city is this pubstomp being held?",
    #                         query_factory=all_cities)

    city = AutocompleteField("City",
                             validators=[Required()],
                             description="In which city is this pubstomp being held?",
                             get_id="geonameid",
                             getter=lambda x: Geoname.get_cities().filter(Geoname.geonameid == x).first()
                             )

    name = TextField("Name", validators=[Required(), Length(max=64)])
    description = TextAreaField("Description", validators=[Optional()],
                                description="Enter some notes about your event. You can use Markdown for formatting here; <a href=\"https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet\" target=\"_blank\">cheatsheet</a>.")
    website = TextField("Website", validators=[Optional(), Length(max=128), URL()])

    venue = FormField(VenueForm)
    days = FieldList(FormField(DayForm), min_entries=1)

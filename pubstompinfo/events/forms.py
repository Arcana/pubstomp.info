from flask.ext.wtf import Form
from wtforms import TextField, IntegerField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import Required, Length, URL, Optional

from ..geo.models import Geoname
from ..leagues.models import League


def all_cities():
    return Geoname.get_cities().order_by(Geoname.country_code, Geoname.name)


def all_leagues():
    return League.query.order_by(League.name)


class EventForm(Form):
    """ Form to edit an event """
    # Event model data
    league = QuerySelectField("League",
                              validators=[Required()],
                              description="Which league is this pubstomp gathering to watch?",
                              query_factory=all_leagues)
    city = QuerySelectField("City",
                            validators=[Required()],
                            description="In which city is this pubstomp being held?",
                            query_factory=all_cities)

    name = TextField("Name", validators=[Required(), Length(max=64)])
    description = TextAreaField("Description", validators=[Optional()])
    website = TextField("Website", validators=[Optional(), Length(max=128), URL()])

    # EventVenue data
    venue_name = TextField("Name", validators=[Optional(), Length(max=64)])
    venue_address1 = TextField("Address 1", validators=[Optional(), Length(max=64)])
    venue_address2 = TextField("Address 2", validators=[Optional(), Length(max=64)])
    venue_capacity = IntegerField("Capacity", validators=[Optional()])

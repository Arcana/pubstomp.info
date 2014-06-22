from .. import db, steam, fs_cache, sentry
from ..dota.models import Schema
import sys
import datetime


class League(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # We'll set this from WebAPI data
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    tournament_url = db.Column(db.String(255))
    itemdef = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    image_url_large = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    events = db.relationship('Event', backref='league', lazy="dynamic")

    def __repr__(self):
        return "{} (league id: {})".format(self.name, self.id)

    def __init__(self, _id=None, name=None, description=None, tournament_url=None, itemdef=None, fetch_images=True):
        self.id = _id
        self.name = name
        self.description = description
        self.tournament_url = tournament_url
        self.itemdef = itemdef

        if fetch_images:
            self.image_url, self.image_url_large = League.fetch_images(self.itemdef)

    @property
    def icon(self):
        if self.image_url is None:
            self.image_url, self.image_url_large = League.fetch_images(self.itemdef)

        return self.image_url

    @property
    def image(self):
        if self.image_url_large is None:
            self.image_url, self.image_url_large = League.fetch_images(self.itemdef)

        return self.image_url_large

    @classmethod
    @fs_cache.cached(timeout=60 * 60, key_prefix="leagues")
    def fetch_leagues_from_webapi(cls):
        """ Fetch a list of leagues from the Dota 2 WebAPI.

        Uses steamodd to interface with the WebAPI.  Falls back to data stored on the file-system in case of a HTTPError
        when interfacing with the WebAPI.

        Returns:
            An array of League objects.
        """
        try:
            res = steam.api.interface("IDOTA2Match_570").GetLeagueListing(language="en_US").get("result")

            # Filter out extra entries with the same league id.
            leagues_by_id = {}
            for _league in res.get("leagues"):
                leagues_by_id[int(_league.get("leagueid"))] = _league

            return leagues_by_id.values()

        except steam.api.HTTPError:
            sentry.captureMessage('League.get_all returned with HTTPError', exc_info=sys.exc_info)

            # Try to get data from existing cache entry
            data = fs_cache.cache.get('leagues', ignore_expiry=True)

            # Return data if we have any, else return an empty list
            return data or list()

    @classmethod
    def update_leagues_from_webapi(cls):
        """ Loops over leagues from WebAPI inserting new data where appropriate. """
        for webapi_league in cls.fetch_leagues_from_webapi():

            # Check if we have a hero entry
            _league = cls.query.filter(cls.id == webapi_league.get('leagueid')).first()

            # If we don't have a hero entry, make a new one
            if not _league:
                _league = cls(
                    webapi_league.get("leagueid"),
                    webapi_league.get("name"),
                    webapi_league.get("description"),
                    webapi_league.get("tournament_url"),
                    webapi_league.get("itemdef")
                )

                # Tell database we want to save it
                db.session.add(_league)

        # Commit all changes to database
        db.session.commit()

    @staticmethod
    def fetch_images(itemdef=None):
        try:
            item_data = Schema.get_by_id(itemdef)
            return item_data.icon, item_data.image
        except KeyError:
            return None, None

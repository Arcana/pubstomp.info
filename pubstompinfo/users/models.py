from .. import db, steam
from flask.ext.login import AnonymousUserMixin
from datetime import datetime


class AnonymousUser(AnonymousUserMixin):
    """
    The anonymous user object for login_manager.  Add any custom methods that the site expects all user's to have here,
    as well as an appropriate value for anonymous users.
    """

    def is_admin(self):
        """
        Whether this user is an admin
        :return: bool
        """
        return False

    def allows_ads(self):
        """
        Whether this user allows advertisements to be shown to them.
        :return: bool
        """
        return True


class User(db.Model):
    """ A user object! Whouda thunk it. """

    # The table name for this model in the database
    __tablename__ = "users"

    # The models columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(64), unique=False, nullable=True)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    admin = db.Column(db.Boolean, default=False)
    show_ads = db.Column(db.Boolean, default=True)

    # Set default order by
    __mapper_args__ = {
        "order_by": [db.asc(first_seen)]
    }

    # Some constants relating to Steam and IDs
    ACCOUNT_ID_TO_STEAM_ID_CORRECTION = 76561197960265728
    ACCOUNT_ID_MASK = 0xFFFFFFFF

    def __init__(self, _id=None, name=None, enabled=True):
        """
        Initialise a new User object, with the data provided.

        :param _id: The user's ID. Defaults to None.
        :param name:  The user's name. Defaults to None.
        :param enabled:  Whether this user account should be abled or disabled.  Defaults to True.
        """
        self.id = _id
        self.name = name
        self.enabled = enabled

    def __repr__(self):
        """
        A string to represent this object - the user's name.
        :return: str
        """
        return self.name

    def get_id(self):
        """
        Returns the user's ID as unicode.  Required by flask-login.
        :return: unicode
        """
        return unicode(self.id)

    def is_active(self):
        """
        Whether this user account is active or not.
        :return: str
        """
        return self.enabled

    def is_anonymous(self):
        """
        Whether this is an anonymous user (noooooooope)
        :return: bool
        """
        return False

    def is_authenticated(self):
        """
        Whether this user is authenticated.
        :return: bool
        """
        return True

    def is_admin(self):
        """
        Whether this user is an admin
        :return: bool
        """
        return self.admin

    def update_last_seen(self):
        """
        Updates this user's `last_seen` datetime and saves it to the database.
        """
        # Called every page load for current_user
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def update_steam_name(self):
        """
        Updates this user's name from Steam, and saves it to the database.
        """
        # Called every page load for current_user (API is cached)
        steam_account_info = steam.user.profile(self.steam_id)
        try:
            if steam_account_info is not None:
                if self.name is not steam_account_info.persona:
                    self.name = steam_account_info.persona
                    db.session.add(self)
                    db.session.commit()
        except steam.api.HTTPError:
            pass

    def allows_ads(self):
        """
        Whether this user allows advertisements to be shown to them.
        :return: bool
        """
        return self.show_ads

    @property
    def steam_id(self):
        """
        This user's ID represented as a 64-bit Steam ID.
        :return: long
        """
        return self.id + User.ACCOUNT_ID_TO_STEAM_ID_CORRECTION

    @staticmethod
    def steam_id_to_account_id(steam_id):
        """
        Method to get an account ID (lower 32-bits) from a steam ID (64 bits)
        :param steam_id: long
        :return: int
        """
        return int(steam_id & User.ACCOUNT_ID_MASK)

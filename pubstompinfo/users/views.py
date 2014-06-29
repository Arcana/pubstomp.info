from flask import Blueprint, render_template, flash, redirect, request, url_for, current_app
from .. import app, oid, steam, db, login_manager, mem_cache, sentry
from models import User, AnonymousUser
from forms import SettingsForm
from flask.ext.login import login_user, logout_user, current_user, login_required

# Create mod
mod = Blueprint("users", __name__, url_prefix="/users")

# Set login manager's anonymous user class.
login_manager.anonymous_user = AnonymousUser


# User authentication
@login_manager.user_loader
def load_user(user_id):
    """
    Loads user details on every request.

    If the user is logged in, their last-seen meta-data will be updated.  This also attempts to update their name on
    the site according to their Steam name, but this only runs once per timeframe specified in the site's config
    (UPDATE_USER_NAME_TIMEOUT)

    :param user_id: A user's ID
    :return: User if we have a user object matching `user_id`.
    :return: None if the user doesn't exist.
    """

    # Fetch user
    _user = User.query.get(user_id)

    # The cache keys for updating the user's Steam name
    _update_name_updated_key = 'update_name_for_user_{}_updated'.format(user_id)
    _update_name_lock_key = 'update_name_for_user_{}_lock'.format(user_id)

    # If we have a user object
    if _user:
        # Update their last-seen meta-data
        _user.update_last_seen()

        # Check whether we can update this user's name
        if not mem_cache.get(_update_name_updated_key) and not mem_cache.get(_update_name_lock_key):
            # Set lock before we do the slow task (prevents concurrent requests all getting stuck on this same task)
            mem_cache.set(_update_name_lock_key, True, timeout=app.config['UPDATE_USER_NAME_TIMEOUT'])

            # Update user's name
            _user.update_steam_name()

            # Set key to say we've updated the name.  We'll re-run this when this key expires
            mem_cache.set(_update_name_updated_key, True, timeout=app.config['UPDATE_USER_NAME_TIMEOUT'])

            # Release lock
            mem_cache.delete(_update_name_lock_key)

    # Return User or None
    return _user


@mod.route('/login/')
@oid.loginhandler
def login():
    """
    Login endpoint for a user.

    Checks if the user is authenticated, if so we redirect them to their next-url, otherwise we sent them to
    "Sign in with Steam".

    :return: Redirect to the user's next-url if the user is logged in.
    :return: Redirect to the Steam Community openid endpoint, if user is not logged in.
    """
    if current_user.is_authenticated():
        return redirect(oid.get_next_url())
    return oid.try_login('http://steamcommunity.com/openid')


@oid.after_login
def create_or_login(resp):
    """
    Handle a user after they have signed in with Steam.

    If the user does not exist in our database, we will create an entry for them and attempt to log them in.
    If the user already exists in our database, we will just attempt to log them in.

    Will flash a message to the user according to their log in attempt:
    - Successful: "Hi you're logged in"
    - Failed, account inactive: "You're account has been disabled".
    - Failed, account active: "Error on our end, try again later pls".

    :param resp: Response from Steam's OpenID endpoint
    :return: Redirect to the user's next-url.
    """

    # Get the user's SteamID from the OpenID response.
    steam_id = long(resp.identity_url.replace("http://steamcommunity.com/openid/id/", ""))

    # Turn that SteamID into an account ID, and get the user with that id.
    account_id = User.steam_id_to_account_id(steam_id)
    _user = User.query.filter(User.id == account_id).first()

    # If a user doesn't exist in our database with that ID, let's register them.
    if not _user:
        _user = User(account_id, steam.user.profile(steam_id).persona or account_id)

        db.session.add(_user)
        db.session.commit()

    # Attempt to log the user in
    login_attempt = login_user(_user)

    # Flash messages according to how that went
    if login_attempt is True:
        flash(u"You are logged in as {}".format(_user.name), "success")
    elif not _user.is_active():
        flash(u"Cannot log you in as {}, your account has been disabled.  If you believe this is in error, please contact {}.".format(_user.name, current_app.config["CONTACT_EMAIL"]), "error")
    else:
        flash(u"Error logging you in as {}, please try again later.".format(_user.name), "error")

    # Rediect the user to their next-url.
    return redirect(oid.get_next_url())


@mod.route('/logout/')
@login_required
def logout():
    """
    Logs a user out of the site.
    :return: Redirect to the user's next-url.
    """
    logout_user()
    return redirect(oid.get_next_url())


@mod.route("/")
@mod.route("/page/<int:page>/")
def users(page=1):
    """
    Paginated view of all the user's on the system.  Restricted to admin only.
    :param page: The page to view. Defaults to 1.
    :return: Response
    """

    # If the user is not an admin, make them go away.
    if not current_user.is_admin():
        flash("User list is admin only atm.", "error")
        return redirect(request.referrer or url_for("index"))

    # Get paginated list of users
    _users = User.query.paginate(page, current_app.config["USERS_PER_PAGE"], False)

    # Render the users list.
    return render_template("users/users.html",
                           title=u"Users listing - {}".format(app.config['SITE_NAME']),
                           users=_users)


@mod.route("/<int:_id>/")
def user(_id):
    """
    A user's profile page. TODO

    :param _id: The user's ID
    :return: Response or redirect to the user's referrer or the site's index.
    """

    # Get the user object
    _user = User.query.filter(User.id == _id).first()

    # If the user doesn't exist flash "User not found" and return the user to their referrer or the site's index.
    if _user is None:
        flash("User {} not found.".format(_id), "error")
        return redirect(request.referrer or url_for("index"))

    # Render user profile
    return render_template("users/user.html",
                           title=u"{} - {}".format(_user.name, app.config['SITE_NAME']),
                           user=_user)


@mod.route("/<int:_id>/update_name")
@login_required
def update_name(_id):
    """
    Admin endpoint to trigger an update of the user's name.

    Will retrieve the new name from Steam, and log the action in Sentry.

    :param _id: The user ID of the user whose name to update.
    :return: Redirect to the visitor's referrer or the site's index.
    """

    # If not an admin, yell at the visitor and redirect them away.
    if not current_user.is_admin():
        flash("Only admins can force-update user names.", "error")
        return redirect(request.referrer or url_for("index"))

    # Get the user object for the given user id.
    _user = User.query.filter(User.id == _id).first()

    # If the user doesn't exist, yell at the visitor and redirect them away.
    if _user is None:
        flash("User {} not found.".format(_id), "error")
        return redirect(request.referrer or url_for("index"))

    # Keep a record of old name and new name, to log.
    old_name = _user.name
    _user.update_steam_name()  # Actually do the update
    new_name = _user.name

    sentry.captureMessage("Manually triggered a user name update.", extra={
        'extra': {
            'user_id': _id,
            'old_name': old_name,
            'new_name': new_name,
            'actioned_by': current_user.id
        }
    })

    # Flash "We did it! WoooooO" and send the visitor home.
    flash(u"Updated user {}'s name from {} to {}.".format(_id, old_name, new_name), "success")
    return redirect(request.referrer or url_for("index"))


@mod.route("/<int:_id>/settings/", methods=["POST", "GET"])
@login_required
def settings(_id):
    """
    A user's settings page.

    Access restricted to the user themselves or admins.

    :param _id: The user ID of the user whose knobs we are tweaking.
    :return: Redirect if shit went wrong.
    :return: Response
    """

    # Check the visitor is the user whose settings we're trying to poke, or an admin.
    if current_user.id != _id and not current_user.is_admin():
        flash("You are not authorised to edit user {}'s settings.".format(_id), "error")
        return redirect(request.referrer or url_for("index"))

    # Get the user object for the given user ID.
    _user = User.query.filter(User.id == _id).first()
    if _user is None:
        flash("User {} not found.".format(_id), "error")
        return redirect(request.referrer or url_for("index"))

    # Get settings form! Woop!
    form = SettingsForm(_user, request.form)

    # If the form was submitted, update the user's settings and send the visitor on their way.
    if form.validate_on_submit():
        _user.email = form.email.data
        _user.show_ads = form.show_ads.data
        db.session.add(_user)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("users.user", _id=_user.id))

    # Render the settings page.
    return render_template("users/settings.html",
                           title="{} - {}".format(
                               "Your settings" if current_user.id == _id else "{}'s settings".format(_user.name),
                               app.config['SITE_NAME']),
                           user=_user,
                           form=form)

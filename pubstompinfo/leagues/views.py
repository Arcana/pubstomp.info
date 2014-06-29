from flask import Blueprint, render_template, current_app, abort
from .. import mem_cache, sentry, db
from models import League
from ..events.models import Event, EventDay
from datetime import datetime

mod = Blueprint("leagues", __name__, url_prefix="/leagues")


@mod.route("/")
@mod.route("/page/<int:page>/")
def leagues(page=1):
    _leagues = League.query.join(Event).\
        filter(Event.days.any(EventDay.end_time > datetime.now())).\
        paginate(page, current_app.config['LEAGUES_PER_PAGE'])
        # group_by(League.id).\
        # order_by(db.func.count(Event.id).desc()).\

    return render_template("leagues/leagues.html",
                           title="Leagues - {}".format(current_app.config['SITE_NAME']),
                           leagues=_leagues)


@mod.before_app_request
def update_leauges():
    _updated_key = 'league_info_updated'
    _lock_key = 'league_info_update_lock'

    # If the last-updated key has expired, and the lock is not set (the lock will be set if another request
    # beat this one to the job)
    if not mem_cache.get(_updated_key) and not mem_cache.get(_lock_key):
        # Set lock before doing expensive task.
        mem_cache.set(_lock_key, True, timeout=current_app.config['UPDATE_LEAGUES_TIMEOUT'])  # Timeout in case the app crashes before it releases the lock.

        # Update hero data
        League.update_leagues_from_webapi()

        # Set key to say we've updated the data.  We'll re-run this process when this key expires
        mem_cache.set(_updated_key, True, timeout=current_app.config['UPDATE_LEAGUES_TIMEOUT'])  # 1 hour timeout

        # Release the lock
        mem_cache.delete(_lock_key)


@mod.route("/<int:_id>/")
def league(_id):
    _league = League.query.filter(League.id == _id).first_or_404()
    return render_template("leagues/league.html",
                           title="{} - {}".format(_league.name, current_app.config['SITE_NAME']),
                           meta_description=u"Dota 2 pubstomps for {} across the world.".format(_league.name),
                           league=_league)

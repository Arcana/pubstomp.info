"""
Manager script :)

Takes the following commands:
- runserver
- shell
"""

from pubstompinfo import app as application, db
from flask.ext.script import Manager

manager = Manager(application)


@manager.command
def update_geonames():
    from pubstompinfo.scripts.update_geonames import update_geonames as _update_geonames
    _update_geonames()

if __name__ == "__main__":
    manager.run()

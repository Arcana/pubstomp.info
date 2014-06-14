"""
Manager script :)

Takes the following commands:
- runserver
- shell
"""

from pubstompinfo import app as application, db
from flask.ext.script import Manager

manager = Manager(application)

if __name__ == "__main__":
    manager.run()

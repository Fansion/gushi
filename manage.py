# -*- coding: utf-8 -*-

from flask.ext.script import Manager, Shell
from gushi import app
from gushi.models import db, Role, User, Story, Upvote, Follow
from flask.ext.migrate import Migrate, MigrateCommand


manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


def make_context():
    return dict(app=app, db=db, User=User, Role=Role, Story=Story, Upvote=Upvote, Follow=Follow)
manager.add_command("shell", Shell(make_context=make_context))


@manager.command
def test():
    """测试"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def run():
    app.run(host='0.0.0.0', debug=True)

if __name__ == '__main__':
    manager.run()

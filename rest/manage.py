from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
import os
from webapp import create_app
from webapp.models import db, Field, User

env = os.environ.get('WEBAPP_ENV','dev')
app = create_app('webapp.config.{}Config'.format(env.capitalize()))
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("server", Server(use_debugger=1))
manager.add_command('db', MigrateCommand)

@manager.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Field=Field)


if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    manager.run()

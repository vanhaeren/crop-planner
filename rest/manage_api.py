from flask_script import Manager, Server
import os
from api import create_app
from api.models import Agrosemens

env = os.environ.get('WEBAPP_ENV','dev')
app = create_app('api.config.{}Config'.format(env.capitalize()))
manager = Manager(app)
manager.add_command("server", Server(use_debugger=1))

@manager.shell
def make_shell_context():
    return dict(app=app, Agrosemens=Agrosemens)


if __name__ == "__main__":
    manager.run()

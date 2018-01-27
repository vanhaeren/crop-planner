from flask import Flask, redirect, url_for, session, request, current_app
from flask_wtf.csrf import CSRFProtect
from webapp.models import db, User, get_or_create
from oauth2client.contrib.flask_util import UserOAuth2
import json
import httplib2

oauth2 = UserOAuth2()
csrf = CSRFProtect()

def create_app(objectname):
    app = Flask(__name__)
    app.config.from_object(objectname)

    db.init_app(app)
       # [START request_user_info]
    def _request_user_info(credentials):
        """
        Makes an HTTP request to the Google+ API to retrieve the user's basic
        profile information, including full name and photo, and stores it in the
        Flask session.
        """
        http = httplib2.Http()
        credentials.authorize(http)
        resp, content = http.request(
            'https://www.googleapis.com/plus/v1/people/me')

        if resp.status != 200:
            current_app.logger.error(
                "Error while obtaining user profile: \n%s: %s", resp, content)
            return None
        session['profile'] = json.loads(content.decode('utf-8'))
        get_or_create(db.session, User, username=session['profile']['displayName'], oauth_client_id=session['profile']['id'])
    # [END request_user_info]

     # [START init_app]
    # Initalize the OAuth2 helper.
    oauth2.init_app(
        app,
        scopes=['email', 'profile'],
        authorize_callback=_request_user_info)
    # [END init_app]

   # [START logout]
    # Add a logout handler.
    @app.route('/logout')
    def logout():
        # Delete the user's profile and the credentials stored by oauth2.
        del session['profile']
        session.modified = True
        oauth2.storage.delete()
        return redirect(request.referrer or '/')
    # [END logout]


    @app.route('/')
    def index():
        return redirect(url_for('planner.field'))

    from webapp.controllers.planner import planner_blueprint
    app.register_blueprint(planner_blueprint)
    csrf.exempt(planner_blueprint)
    app.jinja_env.add_extension('jinja2.ext.do')

    return app


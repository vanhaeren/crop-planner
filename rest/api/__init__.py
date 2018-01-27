from flask import Flask
from api.models import mongo
from api.extensions import (
    rest_api
)
from .controllers.seed import SeedApi

def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)

    rest_api.add_resource(SeedApi, '/api/seed', '/api/seed/<int:page>',endpoint='api')
    mongo.init_app(app)
    rest_api.init_app(app)
    return app
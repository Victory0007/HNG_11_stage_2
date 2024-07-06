from flask import Flask
from flask_jwt_extended import JWTManager
# from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
moment = Moment()


def create_app(config_name):
    app = Flask(__name__)
    app.json.sort_keys = False
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    ma.init_app(app)
    moment.init_app(app)
    jwt.init_app(app)

    # migrate = Migrate(app, db)

    @app.before_request
    def create_tables():
        app.before_request_funcs[None].remove(create_tables)
        # db.drop_all()
        db.create_all()

    from app.resources.user import blp as UserBlueprint
    from app.resources.organization import blp as OrganizationBlueprint
    app.register_blueprint(UserBlueprint)
    app.register_blueprint(OrganizationBlueprint)

    return app

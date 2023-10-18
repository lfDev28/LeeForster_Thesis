
from flask import Flask

from flask_mongoengine import MongoEngine
from flask_celeryext import FlaskCeleryExt
from .celery_utils import make_celery
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

ext_celery = FlaskCeleryExt(create_celery_app=make_celery)
db = MongoEngine()


def create_app(config=None):
    load_dotenv()
    app = Flask(__name__)

    if config is not None:
        app.config.from_object(config)

    # Registering the database

    app.config['MONGODB_SETTINGS'] = {
        'db': "Development",
        'host': 'localhost',
        'port': 27017
    }
    
    db.init_app(app)

    # Registering the celery
    app.config.from_mapping(
        CELERY=dict(
        broker_url="amqp://localhost:5672/",
        result_backend="rpc://",
        task_ignore_result=True
        )
    )

    
    ext_celery.init_app(app)

    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

    jwt = JWTManager(app)
    

    # Registering each route
    from .routes import register_routes
    register_routes(app)

    # Registering the database

    return app




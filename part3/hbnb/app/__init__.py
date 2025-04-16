# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import config  # Import the configuration dictionary
from app.db import db  # Import db instance from app.db

# Initialize extensions
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)

    # Load the configuration based on the environment (default to 'default')
    app.config.from_object(config[config_name])  # Load the config based on 'default'

    # Initialize extensions with the app object
    bcrypt.init_app(app)
    jwt.init_app(app)

    
    db.init_app(app)  # Connect db to the app
    migrate.init_app(app, db)  # Setup migration tool

    # Initialize API
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API')

    # Register namespaces (API routes for different parts of your app)
    from app.api.v1.auth import api as auth_ns
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns

    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    # Optional: Create tables (this will automatically create tables for all models)
    with app.app_context():
        db.create_all()  # This command will create tables for all your models

    return app

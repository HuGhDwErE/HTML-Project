from flask import Flask
from flasgger import Swagger
from app.modules.main.route import main_bp
from app.db.db import db
from sqlalchemy import inspect, text


def initialize_route(app: Flask):
    with app.app_context():
        app.register_blueprint(main_bp, url_prefix='/api/v1/main')


def initialize_db(app: Flask):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        # Upgrade databases created before account roles were introduced.
        columns = {column['name'] for column in inspect(db.engine).get_columns('users')}
        with db.engine.begin() as connection:
            if 'is_admin' not in columns:
                connection.execute(text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE'))
            if 'is_active' not in columns:
                connection.execute(text('ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE'))

def initialize_swagger(app: Flask):
    with app.app_context():
        swagger = Swagger(app)
        return swagger

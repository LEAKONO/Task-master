from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config
from dotenv import load_dotenv
import os

load_dotenv()

migrate = Migrate()
jwt = JWTManager()
mail = Mail()

from models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)

    from auth import bp as auth
    from task import bp as routes
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(routes, url_prefix='/routes')

    @app.route('/')  # Move this route inside the function
    def index():
        return "<h2>Hello, Flask is running!</h2>"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

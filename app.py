from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Initialize extensions without tying them to the app yet
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
db = SQLAlchemy()

def create_app(config_class=Config):
    # Create Flask application
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize the app with each extension
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)

    # Set up logging for debugging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("App initialized with config: %s", config_class)

    # Register blueprints
    from auth import bp as auth
    from task import bp as routes
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(routes, url_prefix='/routes')

    @app.route('/')
    def index():
        return "<h2>Hello, Flask is running!</h2>"

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        logger.info("Database tables created or confirmed existing.")

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

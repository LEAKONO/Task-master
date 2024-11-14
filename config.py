import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    # Database URI (SQLite for local development, PostgreSQL for production)
    if os.getenv('FLASK_ENV') == 'development':
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///task_master.db')  # Default to SQLite if not set
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Use PostgreSQL in production

    # Mail settings
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT', 587)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', False)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

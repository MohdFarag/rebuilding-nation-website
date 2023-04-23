"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """Base config."""
    SECRET_KEY = 'fac1c92dc32f3cec894412ad44efc6035626f019cc497fb36eb3b51ea40d8fc0'
    # SECRET_KEY = environ.get('SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    UPLOAD_FOLDER = "static/UPLOAD/"
    # SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    # DATABASE_URI = environ.get('PROD_DATABASE_URI')


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    # DATABASE_URI = environ.get('DEV_DATABASE_URI')


class Test(Config):
    FLASK_ENV = 'testing'
    TESTING = True
    # DATABASE_URI = environ.get('TEST_DATABASE_URI')
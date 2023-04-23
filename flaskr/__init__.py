"flaskr/__init__.py"

# Packages
import os

from flask import Flask

from flaskr.log import site_logger

from . import db
from . import auth
from . import site

from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
from werkzeug.utils import import_string

#--------------------------------------------------------------------------#

"""Our app"""
# __ init __
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # configuration
    cfg = import_string('flaskr.config.Config')()
    app.config.from_object(cfg)

    if test_config is None:
        # using a development configuration
        # cfg = import_string('flaskr.config.DevConfig')()
        # app.config.from_object(cfg)
        
        # using a production configuration
        cfg = import_string('flaskr.config.ProdConfig')()
        app.config.from_object(cfg)
        app.wsgi_app = ProxyFix(app.wsgi_app)
    else:
        # load the test config if passed in
        app.config.from_object('flaskr.config.Test')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    site_logger.info('Settings are set successfully.')
 
    # Initialize the db File
    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(site.bp)
    app.add_url_rule('/', endpoint='index')

    return app




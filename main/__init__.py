from flask import Flask
import os
from subprocess import Popen
from . import db

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    # todo: move config into separaate non-git-tracked files
    #app.config.from_pyfile('testconfig.py')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import start
    app.register_blueprint(start.bp)

    db.init_app(app)

    return app


app = create_app()

import os

from flask import Flask

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "flaskr.sqlite")
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass
from . import db

db.init_app(app)

# Load the views
from . import core

app.register_blueprint(core.bp)

# Load the config file
app.config.from_object("config.dev")

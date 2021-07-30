# ----------------------------------------------------------------------------#
#                                  Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
# from flask_wtf import Form
# from forms import *
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
#                                App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
#                                 Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
#                                 Imports Routes.
# ----------------------------------------------------------------------------#

from fyyur.routes.general import *
from fyyur.routes.venue import *
from fyyur.routes.artist import *
from fyyur.routes.show import *

# ----------------------------------------------------------------------------#
#                                 Filters.
# ----------------------------------------------------------------------------#

if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")


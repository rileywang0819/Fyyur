from fyyur import db
from datetime import datetime

# ----------------------------------------------------------------------------#
#                                 Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship(
        "Show", 
        backref="venues", 
        lazy=True, 
        cascade="all, delete-orphan" 
        )

    def __repr__(self):
        return f"<Venue {self.id} {self.name}>"


class Artist(db.Model):
    __tablename__ = "artists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship(
        "Show",
        backref="artists",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Artist {self.id} {self.name}>"


class Show(db.Model):
    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(
        db.Integer, 
        db.ForeignKey("artists.id"), 
        nullable=False
    )
    venue_id = db.Column(
        db.Integer, 
        db.ForeignKey("venues.id"), 
        nullable=False
    )
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"<Show {self.artist_id} {self.venue_id} {self.start_time}>"


#----------------------------------------------------------------------------#
#                                  Imports
#----------------------------------------------------------------------------#


import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys


#----------------------------------------------------------------------------#
#                                App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
#                                 Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'
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
    shows = db.relationship('Show', backref='venues', lazy=True)
    UniqueConstraint('name', 'city', 'state', 'address', 'phone',
                     name='unique_name_city_state_address_phone')

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artists'
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
    shows = db.relationship('Show', backref='artists', lazy=True)
    UniqueConstraint('name', 'city', 'state', 'phone',
                     name='unique_name_city_state_phone')

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f'<Show {self.artist_id} {self.venue_id} {self.start_time}>'


#----------------------------------------------------------------------------#
#                                 Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
#                               Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  -------------------------- Venues --------------------------

@app.route('/venues')
def venues():
    """ Shows all venues, grouped by areas(city&state). """
    # use "with_entities()" method to limit the columns to be returned
    areas = Venue.query.with_entities(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    data = []
    for area in areas:
        venues_in_area = Venue.query.filter_by(
            city=area.city, state=area.state).all()
        venues_info = []
        for venue in venues_in_area:
            venue_info = {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all())
            }
            venues_info.append(venue_info)
        area_info = {
            "city": area.city,
            "state": area.state,
            "venues": venues_info
        }
        data.append(area_info)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    """ Search venues with partial string search, case-insensitive. """
    user_input = request.form.get('search_term', '')
    candidates = Venue.query.filter(Venue.name.ilike(f'%{user_input}%'))
    data = []
    count = 0
    for candidate in candidates:
        count += 1
        candidate_info = {
            "id": candidate.id,
            "name": candidate.name,
            "num_upcoming_shows": len(Show.query.filter(Show.venue_id == candidate.id)
                                          .filter(Show.start_time > datetime.now()).all())
        }
        data.append(candidate_info)
    response = {
        "count": count,
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    """ Shows the specific venue's page. """
    venue = Venue.query.filter_by(id=venue_id).first()
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        artist = Artist.query.filter_by(id=show.artist_id).first()
        show_info = {
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if str(show_info["start_time"]) < str(datetime.now()):
            past_shows.append(show_info)
        else:
            upcoming_shows.append(show_info)
    venue_info = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=venue_info)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


# TODO: avoid duplicated(not yet) or nonsensical creation(OK)
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    """ Create a new venue, should avoid duplicated or nonsensical creation. """
    form = VenueForm(meta={"csrf": False})         
    if form.validate_on_submit():  
        error = False
        try:
            new_venue = Venue()
            for field in form:
                setattr(new_venue, field.name, field.data)
            db.session.add(new_venue)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            # give feedback to users with the flashing system
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        else:
            flash('Sorry! Venue ' + request.form['name'] + ' could not be listed!')
        return render_template('pages/home.html')
    else:
        for field_name, error_msg in form.errors.items():
            flash('Error in ' + field_name + ": " + str(error_msg[0]))
        return render_template('errors/500.html', url='/venues/create'), 500


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    
    if venue:
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    else:
        return render_template('errors/404.html'), 404
    
    # for field in form:
    #     # TODO:
    #     print(field.name, field.data)
    # # TODO: populate form with values from venue with ID <venue_id>
    # return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))


# @app.route('/venues/<venue_id>', methods=['DELETE'])
# def delete_venue(venue_id):
#   # TODO: Complete this endpoint for taking a venue_id, and using
#   # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

#   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
#   # clicking that button delete it from the db then redirect the user to the homepage
#   return None


#  -------------------------- Artists --------------------------

@app.route('/artists')
def artists():
    """ Shows all artists. """
    artists = Artist.query.all()
    data = []
    for artist in artists:
        artist_info = {
            "id": artist.id,
            "name": artist.name,
        }
        data.append(artist_info)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    """ Search artists with partial string search, case-insensitive. """
    user_input = request.form.get('search_term', '')
    candidates = Artist.query.filter(Artist.name.ilike(f'%{user_input}%'))
    data = []
    count = 0
    for candidate in candidates:
        count += 1
        candidate_info = {
            "id": candidate.id,
            "name": candidate.name,
            "num_upcoming_shows": len(Show.query.filter(Show.artist_id == candidate.id)
                                          .filter(Show.start_time > datetime.now()).all())
        }
        data.append(candidate_info)
    response = {
        "count": count,
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    """ Shows the specific venue page. """
    artist = Artist.query.filter_by(id=artist_id).first()
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        show_info = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if str(show_info["start_time"]) < str(datetime.now()):
            past_shows.append(show_info)
        else:
            upcoming_shows.append(show_info)
    artist_info = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=artist_info)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


# TODO: avoid duplicated or nonsensical creation
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    """ Creates a new artist. You should avoid duplicated or nonsensical creation. """
    form = ArtistForm(meta={"csrf": False})
    if form.validate_on_submit():
        error = False
        try:
            new_artist = Artist()
            for field in form:
                setattr(new_artist, field.name, field.data)
            db.session.add(new_artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        else:
            flash('Sorry! Artist ' +
                request.form['name'] + ' could not be listed!')
        return render_template('pages/home.html')
    else:
        for field_name, error_msg in form.errors.items():
            flash('Error in ' + field_name + ": " + str(error_msg[0]))
        return render_template('errors/500.html', url='/artists/create'), 500


# @app.route('/artist/<artist_id>', methods=['DELETE'])
# def delete_venue(artist_id):
#   # TODO: Complete this endpoint for taking a artist_id, and using
#   # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

#   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
#   # clicking that button delete it from the db then redirect the user to the homepage
#   return None


#  -------------------------- Shows --------------------------

@app.route('/shows')
def shows():
    """ Displays all shows in chronological order. """
    all_shows = Show.query.join(Venue).join(
        Artist).order_by(Show.start_time).all()
    data = []
    for show in all_shows:
        show_info = {
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        data.append(show_info)

    return render_template('pages/shows.html', shows=data)


# TODO: 未完
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
    form = ShowForm()
    artists_page = '/artists'
    venues_page = '/venues'
    return render_template(
        'forms/new_show.html', 
        form=form, 
        artists_url=artists_page, 
        venues_url=venues_page
    )


# TODO: avoid duplicated or nonsensical creation
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    """ Creates a new show. You should avoid duplicated or nonsensical creation. """
    form = ShowForm(meta={"csrf": False})
    if form.validate_on_submit():
        error = False
        try:
            new_show = Show()
            for field in form:
                setattr(new_show, field.name, field.data)
            db.session.add(new_show)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            flash('Show was successfully listed!')
        else:
            flash('Sorry! Show could not be listed!')
        return render_template('pages/home.html')
    else:
        for field_name, error_msg in form.errors.items():
            flash('Error in ' + field_name + ": " + str(error_msg[0]))
        return render_template('errors/500.html', url='/shows/create'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()


# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

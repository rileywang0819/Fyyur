from fyyur.models import Venue, Artist, Show
from fyyur import db, app
from flask import request, flash, render_template, redirect, url_for, jsonify
from datetime import datetime
from fyyur.forms import ArtistForm
import sys

#  -------------------------- Artists --------------------------

@app.route("/artists")
def artists():
    """Shows all artists."""
    artists = Artist.query.all()
    data = []
    for artist in artists:
        artist_info = {
            "id": artist.id,
            "name": artist.name,
        }
        data.append(artist_info)

    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    """Search artists with partial string search, case-insensitive."""
    user_input = request.form.get("search_term", "")
    candidates = Artist.query.filter(Artist.name.ilike(f"%{user_input}%"))
    data = []
    count = 0
    for candidate in candidates:
        count += 1
        candidate_info = {
            "id": candidate.id,
            "name": candidate.name,
            "num_upcoming_shows": len(
                Show.query.filter(Show.artist_id == candidate.id)
                .filter(Show.start_time > datetime.now())
                .all()
            ),
        }
        data.append(candidate_info)
    response = {"count": count, "data": data}

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    """Shows the specific venue page."""
    artist = Artist.query.filter_by(id=artist_id).first()
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        show_info = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
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

    return render_template("pages/show_artist.html", artist=artist_info)


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    """Creates a new artist. You should avoid duplicated or nonsensical creation."""
    form = ArtistForm(meta={"csrf": False})
    if form.validate_on_submit():
        error = False
        artist = Artist.query.filter(
            Artist.name == form.name.data,
            Artist.city == form.city.data,
            Artist.state == form.state.data,
            Artist.phone == form.phone.data,
        ).first()
        if artist:
            flash(
                form.name.data
                + " already exits. You cannot add the same artist twice !"
            )
            return render_template("pages/home.html")
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
            flash(request.form["name"] + " was successfully listed !")
        else:
            flash("Sorry, " + request.form["name"] + " could not be listed !")
        return render_template("pages/home.html")
    else:
        for field_name, error_msg in form.errors.items():
            flash(str(error_msg[0]))
        return render_template("errors/500.html", url="/artists/create"), 500


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if artist:
        for field in form:
            field.data = getattr(artist, field.name, field.data)
        return render_template("forms/edit_artist.html", form=form, artist=artist)
    return render_template("errors/404.html"), 404


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    form = ArtistForm(meta={"csrf": False})
    if form.validate_on_submit():
        error = False
        artist = Artist.query.get(artist_id)
        try:
            for field in form:
                setattr(artist, field.name, field.data)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            # give feedback to users with the flashing system
            flash(request.form["name"] + " was successfully updated!")
        else:
            flash("Sorry, " + request.form["name"] + " could not be updated!")
        return redirect(url_for("show_artist", artist_id=artist_id))
    else:
        for error_msg in form.errors.items():
            flash(str(error_msg[0]))
        return (
            render_template("errors/500.html", url="/artists/<int:artist_id>/edit"),
            500,
        )


@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    error = False
    artist_name = ""
    try:
        artist = Artist.query.get(artist_id)
        artist_name = artist.name
        db.session.delete(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash(artist_name + " was successfully deleted !")
    else:
        flash("Error occured. " + artist_name + " could not be deleted !")
    return jsonify({'success': True})


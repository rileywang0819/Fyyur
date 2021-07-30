from fyyur.models import Venue, Show, Artist
from fyyur.forms import VenueForm
from datetime import datetime
from flask import render_template, request, flash, redirect, url_for, jsonify
from fyyur import app, db
import sys

#  -------------------------- Venues --------------------------

@app.route("/venues")
def venues():
    """Shows all venues, grouped by areas(city&state)."""
    # use "with_entities()" method to limit the columns to be returned
    areas = (
        Venue.query.with_entities(Venue.city, Venue.state)
        .group_by(Venue.city, Venue.state)
        .all()
    )
    data = []
    for area in areas:
        venues_in_area = Venue.query.filter_by(city=area.city, state=area.state).all()
        venues_info = []
        for venue in venues_in_area:
            venue_info = {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    Show.query.filter(Show.venue_id == venue.id)
                    .filter(Show.start_time > datetime.now())
                    .all()
                ),
            }
            venues_info.append(venue_info)
        area_info = {"city": area.city, "state": area.state, "venues": venues_info}
        data.append(area_info)

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    """Search venues with partial string search, case-insensitive."""
    user_input = request.form.get("search_term", "")
    candidates = Venue.query.filter(Venue.name.ilike(f"%{user_input}%"))
    data = []
    count = 0
    for candidate in candidates:
        count += 1
        candidate_info = {
            "id": candidate.id,
            "name": candidate.name,
            "num_upcoming_shows": len(
                Show.query.filter(Show.venue_id == candidate.id)
                .filter(Show.start_time > datetime.now())
                .all()
            ),
        }
        data.append(candidate_info)
    response = {"count": count, "data": data}

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    """Shows the specific venue's page."""
    print('enter--------------------------')
    venue = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    print(len(venue.shows))
    if venue.shows:
        for show in venue.shows:
            artist = Artist.query.filter_by(id=show.artist_id).first()
            show_info = {
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
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

    return render_template("pages/show_venue.html", venue=venue_info)


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    """Create a new venue, should avoid duplicated or nonsensical creation."""
    form = VenueForm(meta={"csrf": False})
    # avoid nonsensical creation
    if form.validate_on_submit():
        error = False
        # avoid duplicated creation
        venue = Venue.query.filter(
            Venue.name == form.name.data,
            Venue.city == form.city.data,
            Venue.state == form.state.data,
            Venue.address == form.address.data,
            Venue.phone == form.phone.data,
        ).first()
        if venue:
            flash(
                form.name.data
                + " has already exited. You cannot add the same venue twice !"
            )
            return render_template("pages/home.html")
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
            flash(request.form["name"] + " was successfully listed !")
        else:
            flash("Sorry, " + request.form["name"] + " could not be listed !")
        return render_template("pages/home.html")
    else:
        for field_name, error_msg in form.errors.items():
            flash(str(error_msg[0]))
        return render_template("errors/500.html", url="/venues/create"), 500


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if venue:
        for field in form:
            field.data = getattr(venue, field.name, field.data)
        return render_template("forms/edit_venue.html", form=form, venue=venue)
    return render_template("errors/404.html"), 404


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    """Update the specific venue."""
    form = VenueForm(meta={"csrf": False})
    if form.validate_on_submit():
        error = False
        venue = Venue.query.get(venue_id)
        try:
            for field in form:
                setattr(venue, field.name, field.data)
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
        return redirect(url_for("show_venue", venue_id=venue_id))
    else:
        for error_msg in form.errors.items():
            flash(str(error_msg[0]))
        return (
            render_template("errors/500.html", url="/venues/<int:venue_id>/edit"),
            500,
        )


@app.route("/venues/<int:venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    error = False
    venue_name = ""
    try:
        venue = Venue.query.get(venue_id)
        venue_name = venue.name
        print('delete successfully')
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash(venue_name + " was successfully deleted !")
    else:
        flash("Error occured. " + venue_name + " could not be deleted !")
    return jsonify({'success': True})

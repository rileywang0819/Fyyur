from fyyur.models import Venue, Artist, Show
from fyyur import db, app
from flask import flash, render_template
from fyyur.forms import ShowForm
import sys

#  -------------------------- Shows --------------------------

@app.route("/shows")
def shows():
    """Displays all shows in chronological order."""
    all_shows = Show.query.join(Venue).join(Artist).order_by(Show.start_time).all()
    data = []
    for show in all_shows:
        show_info = {
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id)
            .first()
            .image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        data.append(show_info)

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    artists_page = "/artists"
    venues_page = "/venues"
    return render_template(
        "forms/new_show.html",
        form=form,
        artists_url=artists_page,
        venues_url=venues_page,
    )


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    """Creates a new show. You should avoid duplicated or nonsensical creation."""
    form = ShowForm(meta={"csrf": False})
    if form.validate_on_submit():
        error = False
        show = Show.query.filter(
            Show.artist_id == form.artist_id.data,
            Show.venue_id == form.venue_id.data,
            Show.start_time == form.start_time.data,
        ).first()
        if show:
            flash("You cannot add the same show twice !")
            return render_template("pages/home.html")
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
            flash("Show was successfully listed !")
        else:
            flash("Sorry! Show could not be listed !")
        return render_template("pages/home.html")
    else:
        for field_name, error_msg in form.errors.items():
            flash("Error in " + field_name + ": " + str(error_msg[0]))
        return render_template("errors/500.html", url="/shows/create"), 500

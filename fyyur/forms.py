from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, URL, ValidationError, Optional, AnyOf
from fyyur.enums import Genre, State
import re


class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired(message='Invalid time. Please enter again !')],
        default=datetime.today()
    )
    
    def validate_artist_id(self, field):
        if not re.match(r"[0-9]*$", field.data):
            raise ValidationError(
                u"Artist Id should be a number !")
            
    def validate_venue_id(self, field):
        if not re.match(r"[0-9]*$", field.data):
            raise ValidationError(
                u"Venue Id should be a number !")


class VenueForm(FlaskForm):
    name = StringField(
        'name', 
        validators=[DataRequired()]
    )
    city = StringField(
        'city', 
        validators=[DataRequired()]
    )
    state = SelectField(
        'state', 
        validators=[DataRequired()], 
        choices=State.get_state()
    )
    address = StringField(
        'address', 
        validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', 
        validators=[Optional(), URL(message='Invalid image link. Please enter again !')]
    )
    genres = SelectMultipleField(
        'genres', 
        validators=[DataRequired()],
        choices=Genre.get_genres()
    )
    facebook_link = StringField(
        'facebook_link', 
        validators=[Optional(), URL(message='Invalid Facebook link. Please enter again !')],
        default=''
    )
    website_link = StringField(
        'website_link', 
        validators=[Optional(), URL(message='Invalid website link. Please enter again !')],
        default=''
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description'
    )

    def validate_phone(self, field):
        if not re.match(r"^\d{3}-\d{3}-\d{4}$", field.data):
            raise ValidationError(
                u"Please enter phone number in correct format !")


class ArtistForm(FlaskForm):
    name = StringField(
        'name', 
        validators=[DataRequired()]
    )
    city = StringField(
        'city', 
        validators=[DataRequired()]
    )
    state = SelectField(
        'state', 
        validators=[DataRequired()],
        choices=State.get_state()
    )
    phone = StringField(
        'phone',
        validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL(message='Invalid image link. Please enter again !')]
    )
    genres = SelectMultipleField(
        'genres', 
        validators=[DataRequired()],
        choices=Genre.get_genres()
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), URL(message='Invalid Facebook link. Please enter again !')],
        default=''
    )
    website_link = StringField(
        'website_link',
        validators=[Optional(), URL(message='Invalid website link. Please enter again !')],
        default=''
    )
    seeking_venue = BooleanField(
        'seeking_venue'
    )
    seeking_description = StringField(
        'seeking_description'
    )
    
    def validate_phone(self, field):
        if not re.match(r"^\d{3}-\d{3}-\d{4}$", field.data):
            raise ValidationError(
                u"Please enter phone number in correct format !")


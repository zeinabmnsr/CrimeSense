from flask_wtf import FlaskForm 
from wtforms import StringField, HiddenField, TextAreaField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired


class HotspotsForm(FlaskForm):
    crime_type = SelectField("Crime Type", choices=[
        ("Theft", "Theft"),
        ("Assault", "Assault"),
        ("Fraud", "Fraud"),
        ("Other", "Other")
    ], validators=[DataRequired()])

    location = StringField("Location", validators=[DataRequired()])
    danger_time = DateField("Danger Time", format="%Y-%m-%d", validators=[DataRequired()])
    notes = TextAreaField("Notes", validators=[DataRequired()])
    lat = HiddenField("Latitude")
    lng = HiddenField("Longitude")
    submit = SubmitField("Add Hotspot")
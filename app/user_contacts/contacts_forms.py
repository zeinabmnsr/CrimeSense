from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

# Lebanon: +961, 03/70/71/76/78/79...
# UK: +44 or starting with 07
lebanon_regex = r'^(\+961|0)?(3\d{6}|7[0-9]{7}|81\d{6})$'
uk_regex = r'^(\+44\d{10}|07\d{9})$'

class EmergencyContactForm(FlaskForm):
    contact_name = StringField("Contact Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[
        DataRequired(),
        Regexp(f"{lebanon_regex}|{uk_regex}",
               message="Enter a valid Lebanese or UK phone number.")
    ])
    submit = SubmitField("Save")

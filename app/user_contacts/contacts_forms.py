from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import re 


def validate_phone_number(form, field):
    phone = field.data.strip()
    
    # Regex: +961XXXXXXXX or 03XXXXXX or 07XXXXXX or 81XXXXXX
    if not re.match(r"^(\+961\d{7,8}|03\d{6}|07\d{6}|81\d{6})$", phone):
        raise ValidationError("Invalid phone number. Only Lebanese and UK formats are allowed.")


class EmergencyContactForm(FlaskForm):
    name = StringField("Contact Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired(), validate_phone_number])
    submit = SubmitField("Save Contact")
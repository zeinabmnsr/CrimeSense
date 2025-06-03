from flask_wtf import FlaskForm 
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired
from wtforms.fields import DateField 
from flask_wtf.file import FileField, FileAllowed 
from wtforms.validators import DataRequired 

class CrimeReportForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    crime_type = SelectField("Crime Type", choices=[
        ("Theft", "Theft"), ("Assault", "Assault"), ("Fraud", "Fraud"), ("Other", "Other")
    ], validators=[DataRequired()])
    date_occured = DateField("Date Occured", format="%Y-%m-%d", validators=[DataRequired()])
    is_public = BooleanField("Make Public")  # Checkbox for public visibility
    status = SelectField("Status", choices=[
        ("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")
    ], validators=[DataRequired()])
    image = FileField("Upload Image", validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    submit = SubmitField("Submit")
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import ValidationError
from app.models.user import User
from flask import current_app
from bson import ObjectId
from flask_login import current_user

class ProfileUpdateForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    display_name = StringField("Display Name", validators=[Optional(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    location = StringField("Location", validators=[Optional(), Length(max=100)])
    avatar = FileField("Profile Picture", validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField("Update Profile")
    
    def validate_email(self, email):
        """Check if email is already taken by another user."""
        db = current_app.db
        existing_user = db.users.find_one({'email': email.data})
        
        # If user exists and it's not the current user, raise validation error
        if existing_user and str(existing_user['_id']) != current_user.get_id():
            raise ValidationError('This email is already registered. Please choose a different one.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField("Confirm New Password", validators=[
        DataRequired(),
        EqualTo('new_password', message="Passwords must match")
    ])
    submit = SubmitField("Change Password")
    
    def validate_current_password(self, current_password):
        """Verify the current password is correct."""
        db = current_app.db
        user_data = db.users.find_one({'_id': ObjectId(current_user.get_id())})
        
        if not user_data or not User.verify_password(user_data['password'], current_password.data):
            raise ValidationError('Current password is incorrect.')

class ProfileSettingsForm(FlaskForm):
    email_notifications = SelectField("Email Notifications", choices=[
        ('all', 'All Notifications'),
        ('important', 'Important Only'),
        ('none', 'None')
    ], default='all')
    
    privacy_level = SelectField("Profile Privacy", choices=[
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private')
    ], default='public')
    
    location_sharing = SelectField("Location Sharing", choices=[
        ('always', 'Always'),
        ('reports_only', 'Reports Only'),
        ('never', 'Never')
    ], default='reports_only')
    
    language = SelectField("Language", choices=[
        ('en', 'English'),
        ('ar', 'Arabic'),
        ('fr', 'French')
    ], default='en')
    
    submit = SubmitField("Save Settings")

class DeleteAccountForm(FlaskForm):
    password = PasswordField("Enter your password to confirm", validators=[DataRequired()])
    confirmation = StringField("Type 'DELETE' to confirm", validators=[DataRequired()])
    submit = SubmitField("Delete Account")
    
    def validate_password(self, password):
        """Verify the password is correct."""
        db = current_app.db
        user_data = db.users.find_one({'_id': ObjectId(current_user.get_id())})
        
        if not user_data or not User.verify_password(user_data['password'], password.data):
            raise ValidationError('Password is incorrect.')
    
    def validate_confirmation(self, confirmation):
        """Verify the user typed 'DELETE'."""
        if confirmation.data != 'DELETE':
            raise ValidationError('You must type "DELETE" to confirm account deletion.')

class ProfilePictureForm(FlaskForm):
    avatar = FileField("Profile Picture", validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField("Upload Picture")

class ContactInfoForm(FlaskForm):
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=200)])
    website = StringField("Website", validators=[Optional(), Length(max=100)])
    social_media = StringField("Social Media", validators=[Optional(), Length(max=100)])
    submit = SubmitField("Update Contact Info")

class NotificationPreferencesForm(FlaskForm):
    email_reports = SelectField("Report Notifications", choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
        ('none', 'None')
    ], default='immediate')
    
    email_alerts = SelectField("Crime Alert Notifications", choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('none', 'None')
    ], default='immediate')
    
    sms_alerts = SelectField("SMS Alerts", choices=[
        ('emergency', 'Emergency Only'),
        ('all', 'All Alerts'),
        ('none', 'None')
    ], default='emergency')
    
    push_notifications = SelectField("Push Notifications", choices=[
        ('all', 'All Notifications'),
        ('important', 'Important Only'),
        ('none', 'None')
    ], default='all')
    
    submit = SubmitField("Save Preferences")

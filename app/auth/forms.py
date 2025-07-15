from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import re

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=30, message='Password must be at least 8 characters long'),
                 EqualTo('confirm_password', message="Passwords must match")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_password(self, password):
        """Custom password validation for strong password"""
        pwd = password.data
        if len(pwd) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', pwd):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', pwd):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', pwd):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            raise ValidationError('Password must contain at least one special character.')
'''
el super admin yle huwe already aandu acc, 
lhalo fe yaaml register la new admin
aw yaamlo super admin
'''

class AdminRegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[('admin', 'Regular Admin')], default='admin')
    is_super_admin = SelectField('Super Admin', choices=[('no', 'No'), ('yes', 'Yes')], default='no')
    submit = SubmitField('Create Admin')
    
    def validate_password(self, password):
        """Custom password validation for strong password"""
        pwd = password.data
        
        if len(pwd) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', pwd):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', pwd):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', pwd):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
            raise ValidationError('Password must contain at least one special character.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
 
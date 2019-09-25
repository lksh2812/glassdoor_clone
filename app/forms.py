from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
    TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,\
    Length
from app.models import Employee, Employer
from flask import request


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class ReviewForm(FlaskForm):
    review = TextAreaField('Write a Review', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class EditEmployerProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    domain = StringField('Company Domain', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class EditEmployeeProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    work_for = StringField('Current Company', validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationEmployee(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    work_for = StringField('Current Company', validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Employee.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class RegistrationEmployer(FlaskForm):
    username = StringField('Company_name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    domain = StringField('Company Domain', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Employer.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
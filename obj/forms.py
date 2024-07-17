from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional
from butils.iso639 import iso639


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class RegisterForm(FlaskForm):
    submit = SubmitField('Register')

class ibEditForm(FlaskForm):
    id = StringField('ID')
    status = SelectField('Status', choices=[('active', 'Active'), ('archive', 'Archive',), ('offline', 'Offline'),('pending','Pending'),('deleted','Deleted') ], validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    mirrors = StringField('Mirrors', validators=[Optional()])
    language = SelectField('Language', choices=iso639, validators=[DataRequired()])
    software = StringField('Software', validators=[DataRequired()])
    boards = StringField('Boards', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Save')

class ibAddForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    mirrors = StringField('Mirrors', validators=[Optional()])
    language = SelectField('Language', choices=iso639, validators=[DataRequired()])
    software = StringField('Software', validators=[DataRequired()])
    boards = StringField('Boards', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Add')

class ibClaimForm(FlaskForm):
    id = StringField('ID')
    submit = SubmitField('Claim')

class UserEditForm(FlaskForm):
    id = StringField('ID')
    username = StringField('Username')
    role = StringField('Role', validators=[DataRequired()])
    imageboards = StringField('Imageboards', validators=[Optional()])
    submit = SubmitField('Save')
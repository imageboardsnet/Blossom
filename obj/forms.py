from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    submit = SubmitField('Register me!')

class ibEditForm(FlaskForm):
    id = StringField('ID')
    activity = StringField('Activity', validators=[DataRequired()])
    status = SelectField('Status', choices=[('active', 'Active'), ('inactive', 'Inactive',), ('offline', 'Offline'),('pending','Pending'),('deleted','Deleted') ], validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    mirrors = StringField('Mirrors', validators=[Optional()])
    language = StringField('Language', validators=[DataRequired()])
    software = StringField('Software', validators=[DataRequired()])
    favicon = StringField('Favicon', validators=[Optional()])
    boards = StringField('Boards', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Save')

class ibAddForm(FlaskForm):
    activity = StringField('Activity', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    mirrors = StringField('Mirrors', validators=[Optional()])
    language = StringField('Language', validators=[DataRequired()])
    software = StringField('Software', validators=[DataRequired()])
    favicon = StringField('Favicon', validators=[Optional()])
    boards = StringField('Boards', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Add')

class UserEditForm(FlaskForm):
    id = StringField('ID')
    username = StringField('Username')
    role = StringField('Role', validators=[DataRequired()])
    imageboards = StringField('Imageboards', validators=[Optional()])
    submit = SubmitField('Save')

class UserAddForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = StringField('Role', validators=[DataRequired()])
    imageboards = StringField('Imageboards', validators=[Optional()])
    submit = SubmitField('Add')
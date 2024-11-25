from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Optional, Length
from butils.iso639 import iso639


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class RegisterForm(FlaskForm):
    submit = SubmitField('Register')

class ibEditForm(FlaskForm):
    id = StringField('ID')
    status = SelectField('Status', choices=[('active', 'Active'),('pending','Pending'),('archive', 'Archive',),('hiden','Hiden'),('offline', 'Offline'),('deleted','Deleted')], validators=[DataRequired()])
    protocol = SelectField('Protocol', choices=[('https', 'HTTP/S'),('other', 'Other')], validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(),Length(min=3,max=25)])
    url = StringField('URL', validators=[DataRequired(),Length(min=3,max=50)])
    mirrors = StringField('Mirrors', validators=[Optional(),Length(min=3,max=500)])
    language = SelectField('Language', choices=iso639, validators=[DataRequired(),Length(min=1,max=25)])
    software = StringField('Software', validators=[DataRequired(),Length(min=3,max=100)])
    boards = StringField('Boards', validators=[Optional(),Length(min=3,max=500)])
    description = StringField('Description', widget=TextArea(), validators=[Optional(), Length(max=350)],)
    submit = SubmitField('Save')

class ibAddForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(),Length(min=3,max=25)])
    url = StringField('URL', validators=[DataRequired(),Length(min=3,max=50)])
    mirrors = StringField('Mirrors', validators=[Optional(),Length(min=3,max=500)])
    language = SelectField('Language', choices=iso639, validators=[DataRequired(),Length(min=1,max=25)])
    software = StringField('Software', validators=[DataRequired(),Length(min=3,max=100)])
    boards = StringField('Boards', validators=[Optional(),Length(min=3,max=500)])
    description = StringField('Description',widget=TextArea(), validators=[Optional(), Length(max=350)])
    submit = SubmitField('Add')

class ibImportForm(FlaskForm):
    imageboards = StringField('Imageboards', widget=TextArea(), validators=[DataRequired(), Length(min=3,max=5000)])
    submit = SubmitField('Import')

class ibClaimForm(FlaskForm):
    id = StringField('ID')
    submit = SubmitField('Claim')

class UserEditForm(FlaskForm):
    id = StringField('ID')
    username = StringField('Username')
    role = StringField('Role', validators=[DataRequired()])
    imageboards = StringField('Imageboards', validators=[Optional()])
    submit = SubmitField('Save')
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Optional
from dbmanager import load_imageboards, delete_imageboard, get_imageboard, edit_imageboard, check_user, load_user_database, edit_user, remove_user
import secrets

app = Flask(__name__)

app.config['SECRET_KEY'] = "blossom_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EditForm(FlaskForm):
    id = StringField('ID')
    activity = StringField('Activity', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    mirrors = StringField('Mirrors', validators=[Optional()])
    language = StringField('Language', validators=[DataRequired()])
    software = StringField('Software', validators=[DataRequired()])
    favicon = StringField('Favicon', validators=[Optional()])
    boards = StringField('Boards', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Save')

class UsereditForm(FlaskForm):
    id = StringField('ID')
    username = StringField('Username')
    password = PasswordField('Password')
    role = StringField('Role', validators=[DataRequired()])
    imageboards = StringField('Imageboards', validators=[Optional()])
    submit = SubmitField('Save')

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def user_loader(user_id):
    users = load_user_database()
    user = next((user for user in users if str(user['id']) == user_id), None)
    if user:
        loaded_user = User(id=str(user['id']), username=user['username'])
        return loaded_user
    return None

def render_page(title,content):
    if current_user.is_authenticated:
        return render_template('index.html',title=title, content=render_template('navbar.html') + content)
    return render_template('index.html',title=title, content=content)

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    imageboards = load_imageboards()
    return render_page("Blosson | Dashboard", render_template('boards.html', imageboards=imageboards))


@app.route('/dashboard/delete/<int:imageboard_id>')
@login_required
def delete(imageboard_id):
    delete_imageboard(imageboard_id)
    return dashboard()

@app.route('/dashboard/edit/<int:imageboard_id>', methods=['GET', 'POST'])
@login_required
def edit(imageboard_id):
    imageboard = get_imageboard(imageboard_id)
    form = EditForm()
    form.id.data = imageboard["id"]
    form.activity.data = imageboard["activity"]
    form.status.data = imageboard["status"]
    form.name.data = imageboard["name"]
    form.url.data = imageboard["url"]
    form.mirrors.data = imageboard["mirrors"]
    form.language.data = imageboard["language"]
    form.software.data = imageboard["software"]
    form.favicon.data = imageboard["favicon"]
    form.boards.data = imageboard["boards"]
    form.description.data = imageboard["description"]
    if form.validate_on_submit():
        edit_imageboard(imageboard_id, "activity", form.activity.data)
        edit_imageboard(imageboard_id, "status", form.status.data)
        edit_imageboard(imageboard_id, "name", form.name.data)
        edit_imageboard(imageboard_id, "url", form.url.data)
        edit_imageboard(imageboard_id, "mirrors", form.mirrors.data)
        edit_imageboard(imageboard_id, "language", form.language.data)
        edit_imageboard(imageboard_id, "software", form.software.data)
        edit_imageboard(imageboard_id, "favicon", form.favicon.data)
        edit_imageboard(imageboard_id, "boards", form.boards.data)
        edit_imageboard(imageboard_id, "description", form.description.data)
        return redirect(url_for('dashboard'))
    return render_page("Blossom | Edit", render_template('ibedit.html', id=imageboard_id, form=form))

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    users = load_user_database()
    return render_page("Blossom | Users", render_template('users.html', users=users))

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def useredit(user_id):
    users = load_user_database()
    user = next((user for user in users if user['id'] == user_id), None)
    form = UsereditForm()
    form.id.data = user["id"]
    form.username.data = user["username"]
    form.password.data = user["password"]
    form.role.data = user["role"]
    if "imageboards" in user:
        form.imageboards.data = user["imageboards"]
    if form.validate_on_submit():
        edit_user(user_id, "username", form.username.data)
        edit_user(user_id, "password", form.password.data)
        edit_user(user_id, "role", form.role.data)
        edit_user(user_id, "imageboards", form.imageboards.data)
        return redirect(url_for('users'))
    return render_page("Blossom | User Edit", render_template('useredit.html', id=user_id, form=form))

@app.route('/users/delete/<int:user_id>')
@login_required
def userdelete(user_id):
    remove_user(user_id)
    return users()


@app.route('/about')
def about():
    return render_page("Blossom | About", render_template('about.html'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = load_user_database()
        id = check_user(users, form.username.data, form.password.data)
        if id != False:
            user_obj = User(id, form.username.data)
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else :

            flash('Invalid username or password')
    return render_page("Blosson | Login", render_template('login.html', form=form))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run() 

def create_app():
    return app
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from obj.forms import LoginForm, ibEditForm, UserEditForm, UserAddForm
from obj.users import usersb
from obj.imageboards import imageboardsb

app = Flask(__name__)

app.config['SECRET_KEY'] = "blossom_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def user_loader(user_id):
    usersl = usersb()
    user = next((user for user in usersl if str(user['id']) == user_id), None)
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
    imageboardsl = imageboardsb()
    return render_page("Blosson | Dashboard", render_template('boards.html', imageboards=imageboardsl))


@app.route('/dashboard/delete/<int:imageboard_id>')
@login_required
def delete(imageboard_id):
    imageboardsl = imageboardsb()
    imageboardsl.delete_imageboard(imageboard_id)
    return dashboard()

@app.route('/dashboard/edit/<int:imageboard_id>', methods=['GET', 'POST'])
@login_required
def edit(imageboard_id):
    imageboardsl = imageboardsb()
    imageboard = imageboardsl.get_imageboard(imageboard_id)
    form = ibEditForm()
    if request.method == 'GET':
        for field in ["activity", "status", "name", "url", "favicon", "description"]:
            form[field].data = imageboard[field]
        for field in ["mirrors", "language", "software", "boards"]:
            form[field].data = ','.join(imageboard[field])
    if request.method == 'POST':
        if form.validate_on_submit():
            updates = {}
            for field in ["activity", "status", "name", "url", "favicon", "description"]:
                updates[field] = getattr(form, field).data
            for field in ["mirrors", "language", "software", "boards"]:
                updates[field] = [ib.strip() for ib in getattr(form, field).data.split(',')]
            imageboardsl.update_imageboard(imageboard_id, updates)
            return redirect(url_for('dashboard'))
    return render_page("Blossom | Edit", render_template('ibedit.html', id=imageboard_id, form=form))

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    usersl = usersb()
    return render_page("Blossom | Users", render_template('users.html', users=usersl))


@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def useradd():
    form = UserAddForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            usersl = usersb()
            usersl.add_user(form.data['username'], form.data['password'], form.data['role'], form.data['imageboards'])
            return redirect(url_for('users'))
    return render_page("Blossom | Add User", render_template('useradd.html', form=form))

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def useredit(user_id):
    usersl = usersb()
    user = next((user for user in usersl if user['id'] == user_id), None)
    form = UserEditForm()
    if request.method == 'GET':
        form.username.data = user['username']
        form.role.data = user['role']
        if "imageboards" in user:
            form.imageboards.data = ','.join(user['imageboards'])
    if request.method == 'POST':
        if form.validate_on_submit():
            updates = {}
            updates['username'] = form.data['username'] 
            updates['role'] = form.data['role']
            imageboards_str = getattr(form, 'imageboards').data
            updates['imageboards'] = [ib.strip() for ib in imageboards_str.split(',')]
            usersl.edit_user(user_id, updates)
            return redirect(url_for('users'))
    return render_page("Blossom | Edit User", render_template('useredit.html', id=user_id, form=form))

@app.route('/users/delete/<int:user_id>')
@login_required
def userdelete(user_id):
    usersl = usersb()
    usersl.remove_user(user_id)
    return redirect(url_for('users'))

@app.route('/about')
def about():
    return render_page("Blossom | About", render_template('about.html'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usersl = usersb()
        id = usersl.check_user(form.username.data, form.password.data)
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
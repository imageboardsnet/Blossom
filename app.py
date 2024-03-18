from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from obj.forms import LoginForm, RegisterForm, ibEditForm,ibAddForm, UserEditForm, UserAddForm
from obj.users import usersb
from obj.imageboards import imageboardsb
from utils.sauron import check_imageboards, get_status_state, get_status_time, set_status_state
from utils.endpoints import build_endpoints, get_build_date
from utils.utils import time_elapsed_str, verify_hcaptcha
import secrets
import threading

app = Flask(__name__)

app.config['SECRET_KEY'] = "blossom_secret_key"


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

thread_event = threading.Event()

class User(UserMixin):
    def __init__(self, id, username, role,imageboards):
        self.id = id
        self.username = username
        self.role = role
        self.imageboards = imageboards

@login_manager.user_loader
def user_loader(user_id):
    usersl = usersb()
    user = next((user for user in usersl if str(user['id']) == user_id), None)
    if user:
        loaded_user = User(id=str(user['id']), username=user['username'], role=user['role'], imageboards=user['imageboards'])
        return loaded_user
    return None

def render_page(title,content):
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return render_template('index.html',title=title, navbar= render_template('navbar.html', user=current_user.username, admin=True) ,content=content)
        return render_template('index.html',title=title, navbar= render_template('navbar.html', user=current_user.username) ,content=content)
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
    if current_user.role == "admin":
        return render_page("Blosson | Dashboard", render_template('boards.html', imageboards=imageboardsl))
    elif current_user.role == "user":
        userib = [ib for ib in imageboardsl if ib['id'] in current_user.imageboards]
        for ib in imageboardsl:
            for uib in current_user.imageboards:
                if ib['id'] == int(uib):
                    userib.append(ib)
        return render_page("Blosson | Dashboard", render_template('boards.html', imageboards=userib))

@app.route('/dashboard/add', methods=['GET', 'POST'])
@login_required
def add():
    form = ibAddForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not verify_hcaptcha(request.form.get('h-captcha-response')):
                flash('hCaptcha verification failed')
                return render_page("Blossom | Add imageboard", render_template('forms/ibadd.html', form=form))
            imageboardsl = imageboardsb()
            newib = {}
            newib['status'] = "pending"
            for field in ["activity", "name", "url", "favicon", "description"]:
                newib[field] = getattr(form, field).data
            for field in ["mirrors", "language", "software", "boards"]:
                newib[field] = [ib.strip() for ib in getattr(form, field).data.split(',')]
            imageboardsl.add_imageboard(newib)
            if current_user.role == "user":
                userl = usersb()
                print (str(len(imageboardsl)))
                print (current_user.id)
                userl.add_imageboard(current_user.id, str(len(imageboardsl)))
            return redirect(url_for('dashboard'))
    return render_page("Blossom | Add imageboard", render_template('forms/ibadd.html', form=form))

@app.route('/dashboard/delete/<int:imageboard_id>')
@login_required
def delete(imageboard_id):
    if current_user.role == "admin":
        imageboardsl = imageboardsb()
        imageboardsl.delete_imageboard(imageboard_id)
        return dashboard()
    if current_user.role == "user":
        if str(imageboard_id) in current_user.imageboards:
            imageboardsl = imageboardsb()
            update = imageboardsl.get_imageboard(imageboard_id)
            update['status'] = "deleted"
            imageboardsl.update_imageboard(imageboard_id, update)
            return dashboard()

@app.route('/dashboard/edit/<int:imageboard_id>', methods=['GET', 'POST'])
@login_required
def edit(imageboard_id):
    if current_user.role == "user":
        if str(imageboard_id) not in current_user.imageboards:
            return redirect(url_for('dashboard'))
    imageboardsl = imageboardsb()
    imageboard = imageboardsl.get_imageboard(imageboard_id)
    form = ibEditForm()
    if request.method == 'GET':
        for field in ["id","activity", "status", "name", "url", "favicon", "description"]:
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
            if current_user.role == "user":
                updates['status'] = "pending"
            imageboardsl.update_imageboard(imageboard_id, updates)
            return redirect(url_for('dashboard'))
    return render_page("Blossom | Edit imageboard", render_template('forms/ibedit.html', id=imageboard_id, form=form))

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    usersl = usersb()
    return render_page("Blossom | Users", render_template('users.html', users=usersl))


@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def useradd():
    if current_user.role != "admin":
        return redirect(url_for('users'))
    form = UserAddForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            usersl = usersb()
            usersl.add_user(form.data['username'], form.data['password'], form.data['role'], form.data['imageboards'])
            return redirect(url_for('users'))
    return render_page("Blossom | Add User", render_template('forms/useradd.html', form=form))

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def useredit(user_id):
    if current_user.role != "admin":
        return redirect(url_for('users'))
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
            usersl.add_imageboard(user_id, updates['imageboards'])
            return redirect(url_for('users'))
    return render_page("Blossom | Edit User", render_template('forms/useredit.html', id=user_id, form=form))

@app.route('/users/delete/<int:user_id>')
@login_required
def userdelete(user_id):
    if current_user.role != "admin":
        return redirect(url_for('users'))
    usersl = usersb()
    usersl.remove_user(user_id)
    return redirect(url_for('users'))

@app.route('/users/reset/<int:user_id>')
@login_required
def userreset(user_id):
    if current_user.role != "admin":
        return redirect(url_for('users'))
    new_password = secrets.token_urlsafe(16)
    usersl = usersb()
    usersl.set_password(user_id, new_password)
    return render_page("Blossom | Reset Password", render_template('forms/userreset.html',username=usersl.get_username(user_id) , password=new_password))

@app.route('/sauron')
@login_required
def sauron():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    imageboardsl = imageboardsb()
    active_boards = [ib for ib in imageboardsl if ib['status'] == "active"]
    pending_boards = [ib for ib in imageboardsl if ib['status'] == "pending"]
    offline_boards = [ib for ib in imageboardsl if ib['status'] == "offline"]
    last_check_time = get_status_time()
    state = get_status_state()
    time_elapsed_status = time_elapsed_str(last_check_time)
    time_elapsed_build = time_elapsed_str(get_build_date())
    return render_page("Blossom | Sauron", render_template('sauron.html',active_boards=len(active_boards),pending_boards=len(pending_boards), offline_boards=len(offline_boards),total_boards=len(imageboardsl), last_check_time=time_elapsed_status , state=state, build_date=time_elapsed_build))

@app.route('/sauron/run')
@login_required
def sauron_check():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    try:
        thread_event.set()
        thread = threading.Thread(target=check_imageboards)
        thread.start()
        return redirect(url_for('sauron'))
    except Exception as error:
        return redirect(url_for('sauron'))

@app.route('/sauron/stop')
@login_required
def sauron_stop():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    thread_event.clear()
    if get_status_state() == "checking":
        set_status_state("canceled")
    return redirect(url_for('sauron'))

@app.route('/endpoints/build')
@login_required
def endpoints_build():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    build_endpoints()
    return redirect(url_for('sauron'))

@app.route('/initib')
@login_required
def initib():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    imageboardsl = imageboardsb()
    imageboardsl.assign_fields()
    return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    return render_page("Blossom | About", render_template('about.html'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not verify_hcaptcha(request.form.get('h-captcha-response')):
                flash('hCaptcha verification failed')
                return render_page("Blossom | Register", render_template('forms/register1.html', form=form))
            username = secrets.token_urlsafe(3)
            password = secrets.token_urlsafe(16)
            usersl = usersb()
            usersl.add_user(username, password, "user", [])
            return render_page("Blossom | Register", render_template('forms/register2.html', username=username, password=password))
    return render_page("Blossom | Register", render_template('forms/register1.html', form=form))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        if not verify_hcaptcha(request.form.get('h-captcha-response')):
            flash('hCaptcha verification failed')
            return render_page("Blosson | Login", render_template('forms/login.html', form=form))
        usersl = usersb()
        id = usersl.check_user(form.username.data, form.password.data)
        if id != False:
            user_obj = User(id, form.username.data, usersl.get_user(id)['role'], usersl.get_user(id)['imageboards'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else :
            flash('Invalid username or password')
    return render_page("Blosson | Login", render_template('forms/login.html', form=form))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run() 

def create_app():
    return app
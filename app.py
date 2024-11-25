from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from obj.forms import LoginForm, RegisterForm, ibEditForm, ibAddForm, ibClaimForm, UserEditForm, ibImportForm
from obj.users import usersb
from obj.imageboards import imageboardsb
from butils.sauron import check_imageboards
from butils.endpoints import build_endpoints, get_endpoints
from butils.utils import time_elapsed_str, verify_hcaptcha, check_claimed_imageboard, timestamp_to_humane
from butils.favicons import download_favicons
from butils.config import get_var, set_var
import secrets
import threading
import os
import json
from yarl import URL
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)

app.jinja_env.filters['humane_date'] = timestamp_to_humane

app.config['SECRET_KEY'] = get_var('app_secret_key')


data_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

@app.context_processor
def inject_global_vars():
    return {'sitekey': get_var('hcaptcha_sitekey')}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

thread_event = threading.Event()

class ThreadPoolExecutorWrapper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=2)
        return cls._instance

    def submit(self, fn, *args, **kwargs):
        return self.executor.submit(fn, *args, **kwargs)

executor = ThreadPoolExecutorWrapper()

build_endpoints()

class User(UserMixin):
    def __init__(self, id, username, role, imageboards, claim, uuid, creation_date):
        self.id = id
        self.username = username
        self.role = role
        self.imageboards = imageboards
        self.claim = claim
        self.uuid = uuid
        self.creation_date = creation_date

@login_manager.user_loader
def user_loader(user_id):
    usersl = usersb()
    user = next((user for user in usersl if str(user['id']) == user_id), None)
    if user:
        loaded_user = User(id=str(user['id']), username=user['username'], role=user['role'], imageboards=user['imageboards'],claim=user["claim"] ,uuid=user['uuid'], creation_date=user['creation_date'])
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
        return render_page("Dashboard | Blossom", render_template('boards.html', imageboards=imageboardsl))
    elif current_user.role == "user":
        userib = [ib for ib in imageboardsl if ib['id'] in current_user.imageboards]
        for ib in imageboardsl:
            for uib in current_user.imageboards:
                if ib['id'] == int(uib):
                    userib.append(ib)
        return render_page("Dashboard | Blossom", render_template('boards.html', imageboards=userib))

@app.route('/imageboard/claim', methods=['GET', 'POST'])
@login_required
def imageboard_claim():
    form = ibClaimForm()
    imageboardsl = imageboardsb()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not verify_hcaptcha(request.form.get('h-captcha-response')):
                flash('hCaptcha verification failed')
                return render_page("Claim imageboard | Blossom", render_template('forms/ibclaim.html', form=form, imageboard = imageboardsl))
            if current_user.role == "user":
                userl = usersb()
                userl.add_claim(current_user.id, getattr(form, 'id').data)
            return redirect(url_for('myclaims'))
    return render_page("Claim imageboard | Blossom", render_template('forms/ibclaim.html', form=form, useruuid=current_user.uuid, imageboards=imageboardsl))

@app.route('/imageboard/unclaim/<int:imageboard_id>', methods=['GET'])
@login_required
def imageboard_unclaim(imageboard_id):
    if current_user.role == "user":
        userl = usersb()
        userl.remove_claim(current_user.id, str(imageboard_id))
    return redirect(url_for('myclaims'))

@app.route('/imageboard/claim/<int:imageboard_id>', methods=['GET'])
@login_required
def imageboard_claim_ib(imageboard_id):
    if current_user.role == "user":
        if (check_claimed_imageboard(current_user.uuid, imageboard_id)) == True: 
            userl = usersb()
            userl.remove_claim(current_user.id, str(imageboard_id))
            userl.add_imageboard(current_user.id, str(imageboard_id))
            return redirect(url_for('dashboard'))
    return redirect(url_for('myclaims'))

@app.route('/myclaims', methods=['GET'])
@login_required
def myclaims():
    imageboardsl = imageboardsb()
    userib = [ib for ib in imageboardsl if str(ib['id']) in current_user.claim]
    return render_page("My Claimed imageboards | Blossom", render_template('myclaims.html', imageboards=userib, useruuid=current_user.uuid))

@app.route('/imageboard/add', methods=['GET', 'POST'])
@login_required
def imageboard_add():
    form = ibAddForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.role == "user":
                if not verify_hcaptcha(request.form.get('h-captcha-response')):
                    flash('hCaptcha verification failed')
                    return render_page("Add imageboard | Blossom", render_template('forms/ibadd.html', form=form))
            imageboardsl = imageboardsb()
            if imageboardsl.check_if_duplicate(form.data):
                flash('Imageboard already exists')
                return render_page("Add imageboard | Blossom", render_template('forms/ibadd.html', form=form))
            newib = {}
            newib['status'] = "pending"
            newib['protocol'] = 'https'
            for field in ["name", "url", "description"]:
                newib[field] = getattr(form, field).data
            for field in ["mirrors", "language", "software", "boards"]:
                if getattr(form, field).data == "":
                    newib[field] = []
                else:
                    newib[field] = [ib.strip() for ib in getattr(form, field).data.split(',')]
            imageboardsl.add_imageboard(newib)
            if current_user.role == "user":
                userl = usersb()
                userl.add_imageboard(current_user.id, str(imageboardsl.get_last_id()))
            return redirect(url_for('dashboard'))
    return render_page("Add imageboard | Blossom", render_template('forms/ibadd.html', form=form))

@app.route('/imageboard/import',methods=['GET','POST'])
@login_required
def imageboard_import():
    form = ibImportForm()
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if form.validate_on_submit():
            imageboardsl = imageboardsb()
            for url in form.data['imageboards'].split(','):
                try:
                    if url.strip() != "":
                        parsed_url = URL(url)
                        if not parsed_url.host:
                            continue
                            
                        host_parts = parsed_url.host.split('.')
                        if len(host_parts) > 2:
                            name = '.'.join(host_parts[-2:])
                        else:
                            name = parsed_url.host
                        
                        newib = {
                            'name': name,
                            'url': url.strip(),
                            'status': 'pending',
                            'protocol': 'https' if parsed_url.scheme == 'https' else 'other',
                            'mirrors': [],
                            'language': ['eng'],
                            'software': ['unknown'],
                            'boards': [],
                            'description': ''
                        }
                        imageboardsl.add_imageboard(newib)
                except Exception as e:
                    print(f"Error processing URL {url}: {str(e)}")
                    continue
            return redirect(url_for('dashboard'))
    return render_page("Massive Imageboard Import | Blossom", render_template('forms/ibimport.html', form=form))

@app.route('/imageboard/edit/<int:imageboard_id>', methods=['GET', 'POST'])
@login_required
def imageboard_edit(imageboard_id):
    if current_user.role == "user":
        if str(imageboard_id) not in current_user.imageboards:
            return redirect(url_for('dashboard'))
    imageboardsl = imageboardsb()
    imageboard = imageboardsl.get_imageboard(imageboard_id)
    form = ibEditForm()
    if request.method == 'GET':
        for field in ["id", "status","protocol", "name", "url", "description"]:
            form[field].data = imageboard[field]
        for field in ["mirrors", "language", "software", "boards"]:
            form[field].data = ','.join(imageboard[field])
    if request.method == 'POST':
        if form.validate_on_submit():
            updates = {}
            for field in ["status", "name", "url", "description"]:
                updates[field] = getattr(form, field).data
            for field in ["mirrors", "language", "software", "boards"]:
                if getattr(form, field).data == "":
                    updates[field] = []
                else:
                    updates[field] = [ib.strip() for ib in getattr(form, field).data.split(',')]
            if current_user.role == "user":
                if getattr(form, 'status').data == "pending":
                    updates['status'] = "pending"
                else:
                    updates['status'] = "pending-" + getattr(form, 'status').data
            if current_user.role == "admin":
                updates['protocol'] = getattr(form, 'protocol').data
            imageboardsl.update_imageboard(imageboard_id, updates)
            return redirect(url_for('dashboard'))
    return render_page("Edit imageboard | Blossom", render_template('forms/ibedit.html', id=imageboard_id, form=form))

@app.route('/imageboard/status/<int:imageboard_id>', methods=['POST'])
@login_required
def imageboard_status(imageboard_id):
    if current_user.role == "admin":
        imageboardsl = imageboardsb()
        update = imageboardsl.get_imageboard(imageboard_id)
        update['status'] = request.json['status']
        imageboardsl.update_imageboard(imageboard_id, update)
        return json.dumps({'status': 'ok'}), 200
    return ('nok', 200)

@app.route('/imageboard/delete/<int:imageboard_id>')
@login_required
def imageboard_delete(imageboard_id):
    if current_user.role == "admin":
        usersl = usersb()
        for user in usersl:
            if str(imageboard_id) in user['imageboards']:
                usersl.remove_imageboard(user['id'], imageboard_id)
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

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    usersl = usersb()
    return render_page("Users | Blossom", render_template('users.html', users=usersl))

@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
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
    return render_page("Edit User | Blossom", render_template('forms/useredit.html', id=user_id, form=form))

@app.route('/user/delete/<int:user_id>')
@login_required
def user_delete(user_id):
    if current_user.role == "admin" or int(current_user.id) == user_id:
            usersl = usersb()
            usersl.remove_user(user_id)
    return redirect(url_for('users'))

@app.route('/user/reset/<int:user_id>')
@login_required
def user_reset(user_id):
    if current_user.role == "admin" or int(current_user.id) == user_id:
        new_password = secrets.token_urlsafe(16)
        usersl = usersb()
        usersl.set_password(user_id, new_password)
        return render_page("Reset Password | Blossom", render_template('forms/userreset.html',username=usersl.get_username(user_id) , password=new_password))
    return redirect(url_for('users'))

@app.route('/myaccount')
@login_required
def myaccount():
    usersl = usersb()
    user = usersl.get_user(int(current_user.id))
    return render_page("My Account | Blossom", render_template('myaccount.html', user=user))

@app.route('/controlpanel')
@login_required
def controlpanel():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    imageboardsl = imageboardsb()
    active_boards = [ib for ib in imageboardsl if ib['status'] == "active"]
    pending_boards = [ib for ib in imageboardsl if ib['status'] == "pending"]
    offline_boards = [ib for ib in imageboardsl if ib['status'] == "offline"]
    sauron_state = get_var('sauron_state')
    sauron_last_check = time_elapsed_str(get_var('sauron_last_check'))
    favicon_download_date = time_elapsed_str(get_var('favicon_download_date'))
    endpoints_build_date = time_elapsed_str(get_var('endpoint_build_date'))
    return render_page("Control Panel | Blossom", render_template('controlpanel.html',active_boards=len(active_boards),pending_boards=len(pending_boards), offline_boards=len(offline_boards),total_boards=len(imageboardsl), sauron_last_check=sauron_last_check , sauron_state=sauron_state, endpoints_build_date=endpoints_build_date, favicon_download_date=favicon_download_date))

@app.route('/sauron')
@login_required
def sauron():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    imageboardsl = imageboardsb()
    return render_page("Sauron | Blossom", render_template('sauron.html', imageboards=imageboardsl))

@app.route('/sauron/run')
@login_required
def sauron_run():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    try:
        thread_event.set()
        executor.submit(check_imageboards, thread_event)
        return redirect(url_for('controlpanel'))
    except Exception as error:
        print(f"Error starting Sauron: {error}")
        return redirect(url_for('controlpanel'))

@app.route('/sauron/stop')
@login_required
def sauron_stop():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    try:
        thread_event.clear()
        set_var('sauron_state', 'canceled')
        time.sleep(0.5)
        return redirect(url_for('controlpanel'))
    except Exception as error:
        print(f"Error stopping Sauron: {error}")
        return redirect(url_for('controlpanel'))

@app.route('/endpoints/build')
@login_required
def endpoints_build():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    build_endpoints()
    return redirect(url_for('controlpanel'))

@app.route('/favicons/download/<string:type>')
@login_required
def favicons_download(type):
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))
    try:
        thread_event.set()
        if type == "missing":
            executor.submit(download_favicons, True)
        if type == "all":
            executor.submit(download_favicons, False)
        return redirect(url_for('controlpanel'))
    except Exception as error:
        print(f"Error downloading favicons: {error}")
        return redirect(url_for('controlpanel'))

@app.route('/favicons/<int:ib_id>')
def get_favicon(ib_id):
    if not os.path.exists(os.path.join(app.root_path, 'data/favicons', str(ib_id) + '.ico')):
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    return send_from_directory(os.path.join(app.root_path, 'data/favicons'), str(ib_id) + '.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/imageboards.json')
def imageboards_json():
    return get_endpoints()

@app.route('/imageboards_legacy.json')
def imageboards_legacy_json():
    return get_endpoints(legacy=True)

@app.route('/about')
def about():
    return render_page("About | Blossom", render_template('about.html'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if not verify_hcaptcha(request.form.get('h-captcha-response')):
                flash('hCaptcha verification failed')
                return render_page("Register | Blossom", render_template('forms/register1.html', form=form))
            username = secrets.token_urlsafe(3)
            password = secrets.token_urlsafe(16)
            usersl = usersb()
            usersl.add_user(username, password, "user", [],[])
            return render_page("Register | Blossom", render_template('forms/register2.html', username=username, password=password))
    return render_page("Register | Blossom", render_template('forms/register1.html', form=form))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        if not verify_hcaptcha(request.form.get('h-captcha-response')):
            flash('hCaptcha verification failed')
            return render_page("Login | Blossom", render_template('forms/login.html', form=form))
        usersl = usersb()
        id = usersl.check_user(form.username.data, form.password.data)
        if id != False:
            user_obj = User(id, form.username.data, usersl.get_user(id)['role'], usersl.get_user(id)['imageboards'],usersl.get_user(id)['claim'] , usersl.get_user(id)['uuid'],  usersl.get_user(id)['creation_date'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else :
            flash('Invalid username or password')
    return render_page("Login | Blossom", render_template('forms/login.html', form=form))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_page("404 | Blossom", render_template('error.html')), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_page("500 | Blossom", render_template('error.html')), 500

@app.route('/addprotocols')
def add_protocols():
    imageboardsl = imageboardsb()
    imageboardsl.add_protocol()

if __name__ == '__main__':
    app.run() 

def create_app():
    return app
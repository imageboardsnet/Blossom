from flask import Flask, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import secrets

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = secrets.token_hex(16)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
jwt = JWTManager(app)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run() 

def create_app():
    return app
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
import requests
import uuid
import random
import string

auth = Blueprint('auth', __name__)

CLIENT_ID = '924120914767-1c5cdtvpfdtodbv63006m1r5k889vv1n.apps.googleusercontent.com'
CLIENT_SECRET = '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'
GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'
client = WebApplicationClient(CLIENT_ID)

def randomPassword():
    return ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=20))

@auth.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out', category='info')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('passworde')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in', category="success")
                login_user(user, remember=True)
                
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password or email', category="error")
        
        else:
            flash("User does not exist", category="error")


    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm-password')

        user = User.query.filter_by(email=email).first()

        if email == "":
            flash("No email entered", category="error")
        elif user:
            flash("Email already exists", category="error")
        elif len(email) < 4:
            flash('Email is not valid', category='error')
        elif len(password) < 6:
            flash('Password must be greater than 6 characters', category='error')
        elif password != confirm:
            flash('Make sure you entered the same passwords', category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)

            flash('Account created', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/login/google')
def login_with_google():
    google_provider_url, google_provider_state = google_authorization_request()
    return redirect(google_provider_url)

def google_authorization_request():
    google_provider_metadata = requests.get(GOOGLE_DISCOVERY_URL).json()
    google_authorization_endpoint = google_provider_metadata['authorization_endpoint']

    google_provider_state = str(uuid.uuid4())
    request_uri = client.prepare_request_uri(
        google_authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        state=google_provider_state
    )
    return request_uri, google_provider_state

@auth.route('/login/google/callback')
def google_callback():
    google_provider_state = request.args.get('state')
    google_authorization_response = request.url
    google_provider_url = google_authorization_response.split('state')[0].strip('?&')

    google_provider_metadata = requests.get(GOOGLE_DISCOVERY_URL).json()
    google_token_endpoint = google_provider_metadata['token_endpoint']

    google_provider_token_url, headers, body = client.prepare_token_request(
        google_token_endpoint,
        authorization_response=google_authorization_response,
        redirect_url=request.base_url,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    token_response = requests.post(
        google_provider_token_url,
        headers=headers,
        data=body,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    client.parse_request_body_response(token_response.text)
    userinfo_endpoint = google_provider_metadata['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    userinfo_data = userinfo_response.json()

    email = userinfo_data['email']
    print(email)
    user = User.query.filter_by(email=email).first()
    if not user:
        new_user = User(email=email, password=generate_password_hash(str(randomPassword()), method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        user = new_user

        # return redirect(url_for('auth.sign_up'))

    login_user(user, remember=True)
    flash('Logged in with Google', category='success')
    return redirect(url_for('views.home'))
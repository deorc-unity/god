from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

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
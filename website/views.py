from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Linking
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET','POST'])
@login_required
def home():
    if current_user.is_authenticated:
        if request.method == 'POST':
            custom = request.form.get('custom')
            playstore = request.form.get('android')
            appstore = request.form.get('apple')
            fallback = request.form.get('fallback')

            custom_link = Linking.query.filter_by(custom=custom).first()

            if custom == "http://127.0.0.1:5000/":
                flash("Custom URL Not entered", category="error")
            elif custom_link:
                flash("custom-link already exists", category="error")
            elif not playstore == "" and not playstore.startswith('https://play.google.com/store/'):
                flash("Not a valid playstore link", category="error")
            elif not appstore == ""  and not appstore.startswith('https://apps.apple.com/'):
                flash("Not a valid appstore link", category="error")
            elif not fallback == "" and not fallback.startswith("https://"):
                flash("Invalid Link", category="error")
            else:
                new_link = Linking(custom=custom, playstore=playstore, appstore=appstore, fallback=fallback, user_id=current_user.id)
                db.session.add(new_link)
                db.session.commit()
                flash("Link added", category="success")


        return render_template("home.html", user=current_user)
    else:
        return redirect(url_for('auth.login'))

@views.route('/delete-link', methods=['POST'])
def delete_link():
    link = json.loads(request.data)
    linkId = link['linkId']
    link = Linking.query.get(linkId)
    if link:
        if link.user_id == current_user.id:
            db.session.delete(link)
            db.session.commit()
    return jsonify({})
    
@views.route('/<path:path>', methods=['GET'])
def redirect_to_link(path):
    full_url = request.url
    print(full_url)
    link = Linking.query.filter_by(custom=full_url).first()
    if link:
        user_agent = request.user_agent.string
        print("User Agent", user_agent)
        # if 'Safari' in user_agent:
        #     print("Yes")
        print(link.appstore)
        print(link.playstore)
        print(link.fallback)
        if link.appstore == "" and link.playstore == "":
            if link.fallback == "":
                redirect('home.html')
            else:
                return redirect(link.fallback)

        elif 'Android' in user_agent or 'Windows' in user_agent:
            print("Here play")
            redirect_link = link.playstore
        elif 'iPhone' in user_agent or 'iPad' in user_agent or 'Macintosh' in user_agent:
            print(not link.appstore == "")
            print("here app")
            redirect_link = link.appstore
        else:
            print("OMG")
            redirect_link = link.fallback

        return redirect(redirect_link)
    else:
        flash("Custom link not found", category="error")
        return redirect('/')

@views.route('/update-link', methods=['POST'])
def update_link():
    data = json.loads(request.data)
    link_id = data['linkId']
    custom = data['custom']
    playstore = data['android']
    appstore = data['apple']
    fallback = data['fallback']

    if not custom or custom == "http://127.0.0.1:5000/":
        return jsonify({'message': 'Custom URL cannot be empty'}), 400
    elif not playstore == "" and not playstore.startswith('https://play.google.com/store/'):
        return jsonify({'message': 'Invalid Playstore link'}), 400
    elif not appstore == ""  and not appstore.startswith('https://apps.apple.com/'):
        return jsonify({'message': 'Invalid appstore link'}), 400
    elif not fallback == "" and not fallback.startswith("https://"):
        return jsonify({'message': 'Invalid fallback link'}), 400

    # existing_link = Linking.query.filter_by(custom = custom).first()
    # if existing_link:
    #     return jsonify({'message': 'Custom URL already exists'}), 400

    link = Linking.query.get(link_id)
    if link:
        if link.user_id == current_user.id:
            link.custom = custom
            link.playstore = playstore
            link.appstore = appstore
            link.fallback = fallback
            db.session.commit()
            flash("Link updated successfully", category="success")
            return jsonify({'message': 'success'})
        else:
            return jsonify({'message': 'Unauthorized'}), 403
    else:
        return jsonify({'message': 'Link not found'}), 404
    
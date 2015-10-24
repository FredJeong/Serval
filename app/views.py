#-*-coding: utf-8 -*-
from app import config, app, api, db, models, lm
from flask import render_template, Response, redirect, url_for, request, abort, session
from flask.ext.restful import Resource, reqparse, fields, marshal_with

from mongoengine.queryset import DoesNotExist

from flask.ext.login import login_user, logout_user, current_user, \
    login_required, AnonymousUserMixin

from flask_oauth import OAuth

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.SOCIAL_FACEBOOK['consumer_key'],
    consumer_secret=config.SOCIAL_FACEBOOK['consumer_secret'],
    request_token_params={'scope': ('email, ')}
)

@lm.user_loader
def load_user(id):
    return models.User.objects(facebook_id=id)

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@app.route('/facebook_login')
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@app.route('/facebook_authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')

    data = facebook.get('/me').data
    if 'id' in data:
        user_id = data['id']
    user = models.User.objects(facebook_id=user_id).first()
    if user is None:
        user = models.User(facebook_id=user_id)
        user.save()

    login_user(user)

    return redirect(next_url)

@app.route('/logout')
def logout():
    pop_login_session()
    return redirect(url_for('index'))

@app.route('/')
def index():
    user_id = None
    user_name = None
    if 'logged_in' in session and session['logged_in']:
        data = facebook.get('/me').data
        if 'id' in data and 'name' in data:
            user_id = data['id']
            user_name = data['name']
    return render_template(
        'index.html',
        session=session,
        user_id=user_id, user_name=user_name)
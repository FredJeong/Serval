#-*-coding: utf-8 -*-
from app import config, app, api, db, models, lm, forms
from flask import render_template, Response, redirect, url_for, request, abort, session
from flask.ext.restful import Resource, reqparse, fields, marshal_with

from mongoengine.queryset import DoesNotExist
from mongoengine import ValidationError

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
    return models.User.objects(facebook_id=id).first()

@app.errorhandler(404)
def not_found(e):
    return "HTTP 404 NOT FOUND"

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)
    session.pop('user_id', None)
    session.pop('user_name', None)

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
    if 'id' in data and 'name' in data:
        session['user_id'] = data['id']
        session['user_name'] = data['name']
    user = models.User.objects(facebook_id=session['user_id']).first()
    if user is None:
        user = models.User(facebook_id=session['user_id'])
        user.save()
    if user.name != session['user_name']:
        user.name = session['user_name']
        user.save()
    login_user(user)

    return redirect(next_url)

@app.route('/logout')
def logout():
    pop_login_session()
    return redirect(url_for('index'))

@app.route('/')
def index():
    petitions = None
    if 'logged_in' in session and session['logged_in']:
        user = models.User.objects(facebook_id=session['user_id']).first()
        petitions = models.Petition.objects(author=user)
    return render_template(
        'index.html',
        session=session,
        petitions=petitions)

@app.route('/petition/create')
def add_petition():
    form = forms.PetitionForm()
    return render_template(
        'add_petition.html',
        session=session,
        form=form)

@app.route('/petition/<string:uid>')
def view_petition(uid):
    try:
        petition = models.Petition.objects(id=uid).first()
    except ValidationError:
        print("Petition ID invalid")
        abort(404)
    if petition is None:
        abort(404)

    return render_template(
        'petition.html',
        session=session,
        petition=petition)



class Petition(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=unicode)
        parser.add_argument('content', type=unicode)
        parser.add_argument('items[]', dest='items', type=unicode, action='append')

        args = parser.parse_args()
        items = map(lambda x: x.split('|', 1), args['items'])
        items = map(lambda x:
            models.Item(target_fund=int(x[0]), description=x[1]).save(),
            items)
        petition = models.Petition(
            title=args['title'], content=args['content'],
            items=items)
        petition.save()
        user = models.User.objects(facebook_id=session['user_id']).first()
        petition.author = user
        petition.save()


        return petition.__dict__(), 201

    def get(self, uid):
        obj = models.Petition.objects(id=uid).first()
        if obj is None:
            return None, 404
        return obj.__dict__(), 200

class Donation(Resource):
    def put(self, uid):
        parser = reqparse.RequestParser()
        parser.add_argument('balance', type=int)
        parser.add_argument('message', type=unicode)
        args = parser.parse_args()
        item = models.Item.objects(id=uid).first()
        if item is None:
            abort(404)

        donation = models.Donation(
            balance=args['balance'], message=args['message'])
        user = models.User.objects(facebook_id=session['user_id']).first()
        donation.user = user
        item.current_fund += args['balance']
        item.donations.append(donation)
        item.save()

        return item.__dict__(), 200

api.add_resource(Petition, '/api/petition', '/api/petition/<string:uid>')
api.add_resource(Donation, '/api/item/<string:uid>/fund')
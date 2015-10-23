#-*-coding: utf-8 -*-
from flask import Flask

from flask.ext import restful

from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager


import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://be3278fbbccac7:64de4292@us-cdbr-iron-east-01.cleardb.net/heroku_60fb971363678a5'
app.config.from_object('app.config')

db = MongoEngine(app)
api = restful.Api(app)
lm = LoginManager()
lm.init_app(app)

from app import views, models, forms, config

#-*- coding: utf-8 -*-
from flask import redirect, url_for, request
from flask.ext.login import current_user
from flask.ext.wtf import Form

from wtforms import IntegerField, TextField, PasswordField, HiddenField, \
    TextAreaField, FormField, FieldList, SubmitField, validators

from app import app, models, db

class ItemForm(Form):
    description = TextField(u'선물', default='')
    target_fund = IntegerField(u'목표 금액')

class PetitionForm(Form):
    title = TextField(u'제목')
    content = TextAreaField(u'내용')
    items = FieldList(FormField(ItemForm))
    submit = SubmitField()
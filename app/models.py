#-*- coding: utf-8-*-
from app import db
from mongoengine import *
import datetime
from helper import to_timestamp

class User(db.Document):
    facebook_id = LongField(unique=True)
    name = StringField()
    friends = ListField(ReferenceField('User'))
    profile = StringField()
    first_name = StringField()

    def update_friends(self, friends):
        #Check if it works; to prevent excessive query
        #if len(self.friends) == len(friends):
        #    return
        friends = map(lambda x:x['id'], friends['data'])
        self.friends = self.__class__.objects(facebook_id__in=friends)
        self.save()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.facebook_id)

    def __repr__(self):
        return "User: " + self.get_id()

class Donation(db.EmbeddedDocument):
    user = ReferenceField(User)
    balance = IntField(required=True)
    message = StringField()
    secret = BooleanField()
    pending = BooleanField(default=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

    def __dict__(self):
        return {
            'user' :self.user.__repr__(),
            'balance': self.balance,
            'message': self.message,
            'pending': self.pending,
            'secret': self.secret,
            'timestamp': to_timestamp(self.timestamp)
        }
class Item(db.Document):
    target_fund = IntField(required=True)
    current_fund = IntField(required=True, default=0)
    pending_fund = IntField(required=True, default=0)
    donations = ListField(EmbeddedDocumentField(Donation))
    description = StringField(default='')
    recommended_funding = IntField()

    def __dict__(self):
        return {
            'id': str(self.id),
            'description': self.description,
            'target_fund': self.target_fund,
            'current_fund': self.current_fund
        }

    def update_fund(self):
        self.current_fund = 0
        self.pending_fund = 0
        for donation in self.donations:
            if donation.pending:
                self.pending_fund += donation.balance
            else:
                self.current_fund += donation.balance

class Petition(db.Document):
    author = ReferenceField(User)
    title = StringField()
    content = StringField()
    items = ListField(ReferenceField(Item))
    timestamp = DateTimeField(default=datetime.datetime.now)
    due = DateTimeField()
    video_link = StringField()
    cover_link = StringField()



    def __dict__(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'author': self.author.__repr__(),
            'timestamp': to_timestamp(self.timestamp),
            'items': map(lambda x:x.__dict__(), self.items)
        }

    def fund_total(self):
        target_fund = 0
        current_fund = 0
        pending_fund = 0
        for item in self.items:
            target_fund += item.target_fund
            current_fund += item.current_fund
            pending_fund += item.pending_fund
        return (target_fund, current_fund, pending_fund)

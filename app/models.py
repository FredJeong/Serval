from app import db
from mongoengine import *
import datetime

class User(db.Document):
    facebook_id = LongField(unique=True)
    name = StringField()

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

class Item(db.Document):
    target_fund = IntField(required=True)
    current_fund = IntField(required=True, default=0)
    donations = ListField(EmbeddedDocumentField(Donation))
    description = StringField(default='')

    def __dict__(self):
        return {
            'id': str(self.id),
            'description': self.description,
            'target_fund': self.target_fund,
            'current_fund': self.current_fund
        }

class Petition(db.Document):
    author = ReferenceField(User)
    title = StringField()
    content = StringField()
    items = ListField(ReferenceField(Item))
    timestamp = DateTimeField(default=datetime.datetime.now)

    def __dict__(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'author': self.author.__repr__(),
            'timestamp': (self.timestamp - datetime.datetime(1970,1,1)).total_seconds(),
            'items': map(lambda x:x.__dict__(), self.items)
        }

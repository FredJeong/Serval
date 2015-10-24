from app import db
from mongoengine import IntField, BooleanField, DateTimeField, \
    MultiLineStringField, StringField

class User(db.Document):
    facebook_id = IntField(unique=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.facebook_id)
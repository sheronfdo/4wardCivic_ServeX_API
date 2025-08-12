from mongoengine import Document, StringField, EmailField, ReferenceField
from app.models.media import Media

class Authority(Document):
    authorityName = StringField(required=True)
    email = EmailField(required=True, unique=True)
    address = StringField(required=True)
    phoneNumber = StringField(required=True)
    hotline = StringField(required=True)
    authorityIconId = ReferenceField(Media)  # Optional reference to Media

    meta = {
        'collection': 'authorities'
    }
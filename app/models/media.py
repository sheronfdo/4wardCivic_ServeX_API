from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class Media(Document):
    file_path = StringField(required=True)
    file_name = StringField(required=True)
    uploaded_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'media'
    }
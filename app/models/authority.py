from mongoengine import Document, StringField, EmailField, ReferenceField, BooleanField
from app.models.media import Media
from app.models.status import STATUS


class Authority(Document):

    authorityName = StringField(required=True)
    email = EmailField(required=True, unique=True)
    address = StringField(required=True)
    phoneNumber = StringField(required=True)
    hotline = StringField(required=True)
    authorityIconId = ReferenceField(Media)
    verification_token = StringField()
    is_verified = BooleanField(default=False)
    status = StringField(required=True, choices=STATUS)

    meta = {
        'collection': 'authorities',
        'indexes': ['email']
    }

    def to_dict(self):
        return {
            "id": str(self.id),
            "authorityName": self.authorityName,
            "authorityIcon": self.authorityIconId.to_dict() if self.authorityIconId else None
        }
    
    def __str__(self):
        return f'<Authority {self.authorityName}>'


    
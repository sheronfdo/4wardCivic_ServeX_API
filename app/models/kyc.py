from mongoengine import Document, StringField, ReferenceField

from app.models.status import STATUS


class Kyc(Document):
    citizen_id = ReferenceField('User' , required=True)
    id_type = StringField(required=True)
    id_number = StringField(required=True)
    id_front_image = ReferenceField('Media',required=True)
    id_back_image = ReferenceField('Media',required=True)
    user_video = ReferenceField('Media',required=True)
    status = StringField(choices=STATUS, required=True)

    meta = {
        'collection': 'kyc'
    }

    def to_dict(self):
        return {
            "id": str(self.id),
            "citizen_id": str(self.citizen_id.id),
            "id_type": self.id_type,
            "id_number": self.id_number,
            "id_front_image": str(self.id_front_image.id),
            "id_back_image": str(self.id_back_image.id),
            "user_video": str(self.user_video.id),
            "status": self.status
        }

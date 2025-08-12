from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class Media(Document):
    file_path = StringField(required=True)
    file_name = StringField(required=True)
    uploaded_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'media'
    }

    def to_dict(self):
        return {
            "id": str(self.id),
            "file_path": self.file_path,
            "file_name": self.file_name,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }

    def __str__(self):
        return f"<Media {self.file_name}>"
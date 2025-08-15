from mongoengine import Document, IntField, EmbeddedDocument,EmbeddedDocumentListField,StringField, ListField, BooleanField, DateTimeField, DictField, ReferenceField
from datetime import datetime
from app.models.service import Service
from app.models.status import STATUS
from app.models.user import User 


class ServiceRequested(Document):
    user = ReferenceField(User, required=True)
    service = ReferenceField(Service, required=True)
    appoiment_Date = DateTimeField(required=True) 
    slot_start_time = DateTimeField(required=True)
    slot_end_time = DateTimeField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    status = StringField(required=True, choices=STATUS)

    meta = {
        'collection': 'service_requested',
        'indexes': ['service', 'status', 'created_at']
    }
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(ServiceRequested, self).save(*args, **kwargs)

    def to_dict(self):
        """Convert ServiceRequested object to dictionary for MongoDB storage"""
        return {
            "id": str(self.id),
            "appoiment_Date":self.appoiment_Date.isoformat() if self.appoiment_Date else None,
            "service_id": str(self.service.id) if self.service else None,
            "status": self.status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    def validate_service_requested_data(self):
        """Validate service requested data before saving"""
        errors = []

        if not self.user :
            errors.append("service requested user is required")

        if not self.service :
            errors.append("service is required")

        return errors
from mongoengine import Document, StringField, EmbeddedDocument,EmbeddedDocumentListField,FloatField, IntField, BooleanField, DateTimeField, ReferenceField, PULL
from datetime import datetime
from app.models.status import STATUS
from app.models.staff_roll import StaffRoll
from app.models.service import Service

class SubProcess(EmbeddedDocument):
    process_name = StringField(required=True)
    assignedRole = ReferenceField('StaffRoll', required=True)
    order = IntField(required=True)
    status = StringField(required=True, choices=STATUS, default='ACTIVE')

class Process(Document):
    processes = EmbeddedDocumentListField(SubProcess)
    service = ReferenceField(Service)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    
    meta = {
        'collection': 'process',
        'indexes': ['service', 'processes', 'created_at']
    }
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Process, self).save(*args, **kwargs)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "process_name": self.process_name,
            "assignedRole": str(self.assignedRole.staffroll) if self.assignedRole else None,
            "service":str(self.service.id) if self.service else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            
        }
    
from mongoengine import Document, StringField, FloatField, IntField, BooleanField, DateTimeField, ReferenceField, PULL
from datetime import datetime
from app.models.media import Media
from app.models.authority import Authority

class Service(Document):
    service_name = StringField(required=True, max_length=255)
    note = StringField()
    service_fee_lrk = FloatField(required=True, default=0.0)
    start_time = StringField(required=True)
    end_time = StringField(required=True)
    slot_duration = IntField(required=True)  # in minutes
    max_people_per_slot = IntField(required=True, default=1)
    kyc = BooleanField(default=False)
    physicalAttendance = BooleanField(default=False)
    service_icon = ReferenceField(Media, reverse_delete_rule=PULL)
    authority = ReferenceField(Authority)
    status = StringField(default="Active", choices=["Active", "Inactive"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    
    meta = {
        'collection': 'services',
        'indexes': ['service_name', 'status', 'created_at']
    }
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Service, self).save(*args, **kwargs)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "service_name": self.service_name,
            "note": self.note,
            "service_fee_lrk": self.service_fee_lrk,
            "start_time": self.start_time if self.start_time else None,
            "end_time": self.end_time if self.end_time else None,
            "slot_duration": self.slot_duration,
            "max_people_per_slot": self.max_people_per_slot,
            "kyc": self.kyc,
            "physicalAttendance": self.physicalAttendance,
            "service_icon_id": str(self.service_icon.id) if self.service_icon else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "service_icon": self.service_icon.to_dict() if self.service_icon else None
        }
    
    def __str__(self):
        return f'<Service {self.service_name}>'
"""
staff roll model using MongoEngine
"""
from datetime import datetime
from mongoengine import Document, StringField, EmailField, DateTimeField, BooleanField,ReferenceField
from app.models.authority import Authority
from app.models.status import STATUS


class StaffRoll(Document):
    """StaffRoll document model"""
    
    # Fields
    staffroll = StringField(required=True, max_length=200)
    authority = ReferenceField(Authority, required=True)
    status = StringField(required=True, choices=STATUS, default='ACTIVE')
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()
    
    # Meta configuration
    meta = {
        'collection': 'staff_rolls',  # Changed collection name to be more descriptive
        'indexes': ['staffroll', 'created_at'],
        'ordering': ['-created_at']
    }
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.save()
    
    def to_dict(self):
        """Convert staff roll to dictionary"""
        data = {
            'id': str(self.id),
            'staffroll': self.staffroll,
            'authority': str(self.authority.id) if self.authority else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }   
        return data
    
    def validate_staff_roll(self):
        """Validate staff roll data before saving"""
        errors = []

        if not self.staffroll or not self.staffroll.strip():
            errors.append("Staff roll name is required")
        
        if not self.authority:
            errors.append("Authority is required")
        
        if not self.status:
            errors.append("Status is required")

        return errors

    def __str__(self):
        return f"StaffRoll({self.staffroll}, {self.authority})"
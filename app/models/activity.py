from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime

class Activity(Document):
    """Activity model for tracking system activities"""
    
    # Basic fields
    description = StringField(max_length=500, required=True)
    status = StringField(max_length=50, choices=['Pending', 'Completed', 'Failed', 'In Progress'], default='Pending')
    timestamp = DateTimeField(default=datetime.utcnow)
    
    # Reference to authority (assuming you have an Authority model)
    authority = ReferenceField('Authority', required=False)
    
    # Reference to user who performed the activity
    user = ReferenceField('User', required=False)
    
    # Reference to service if activity is related to a service
    service = ReferenceField('Service', required=False)
    
    # Activity type for categorization
    activity_type = StringField(max_length=100, choices=[
        'Service Created', 'Service Updated', 'Service Deleted',
        'User Login', 'User Logout', 'System Update',
        'Data Export', 'Data Import', 'Other'
    ], default='Other')
    
    # Additional metadata as JSON
    metadata = StringField(required=False)  # Can store JSON string for additional data
    
    meta = {
        'collection': 'activities',
        'indexes': [
            'timestamp',
            'authority',
            'status',
            'activity_type',
            ('authority', '-timestamp'),  # Compound index for authority-based queries
        ],
        'ordering': ['-timestamp']  # Default ordering by newest first
    }
    
    def to_dict(self):
        """Convert activity to dictionary"""
        return {
            'id': str(self.id),
            'description': self.description,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'activity_type': self.activity_type,
            'authority_id': str(self.authority.id) if self.authority else None,
            'user_id': str(self.user.id) if self.user else None,
            'service_id': str(self.service.id) if self.service else None,
            'metadata': self.metadata
        }
    
    def __str__(self):
        return f"{self.activity_type}: {self.description} - {self.status}"
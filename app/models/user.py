"""
User model using MongoEngine
"""
from datetime import datetime
from mongoengine import Document, StringField, EmailField, DateTimeField, BooleanField,ReferenceField
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.authority import Authority
from app.models.status import STATUS


class User(Document):
    """User document model"""
    
    # User role choices
    ROLES = ('GovAdmin', 'User')
    
    # Fields
    name = StringField(required=True, max_length=100)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(max_length=20, choices=ROLES, default='User')
    authority = ReferenceField(Authority, required=True)
    is_active = BooleanField(default=True)
    verification_token = StringField()
    is_verified = BooleanField(default=False)
    status = StringField(required=True, choices=STATUS)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()
    
    # Meta configuration
    meta = {
        'collection': 'users',
        'indexes': ['email', 'role', 'created_at'],
        'ordering': ['-created_at']
    }
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.save()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['password'] = self.password
            
        return data
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'GovAdmin'

    
    def clean(self):
        """Clean and validate data before saving"""
        self.email = self.email.lower().strip() if self.email else ''
        self.name = self.name.strip() if self.name else ''
        self.updated_at = datetime.utcnow()

        if self.role != 'GovAdmin':
            self.authority = None
        elif not self.authority:
         raise ValueError("Admin role requires an authority.")

    
    def __str__(self):
        return f"User(email={self.email}, role={self.role})"
    
    def __repr__(self):
        return f"<User {self.email}>"
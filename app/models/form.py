from mongoengine import Document, StringField, ListField, BooleanField, DateTimeField, DictField
from datetime import datetime
from app.models.media import Media

class Form(Document):
    title = StringField(required=True, max_length=255)
    description = StringField()
    questions = ListField(DictField())  # Changed to store dictionaries for each question
    is_active = BooleanField(default=True)
    created_by = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'forms',
        'indexes': ['title', 'is_active', 'created_at']
    }
    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Form, self).save(*args, **kwargs)
    
    def to_dict(self):
        """Convert Form object to dictionary for MongoDB storage"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "questions": self.questions,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def validate_form_data(self):
        """Validate form data before saving"""
        errors = []
        
        if not self.title or not self.title.strip():
            errors.append("Form title is required")
        
        if not self.questions or len(self.questions) == 0:
            errors.append("At least one question is required")
        
        for i, question in enumerate(self.questions):
            question_errors = self._validate_question(question, i)
            errors.extend(question_errors)
        
        return errors

    def _validate_question(self, question, index):
        """Validate individual question"""
        errors = []
        question_types = [
            'multiple-choice', 'checkboxes', 'dropdown', 
            'short-answer', 'paragraph', 'linear-scale', 
            'date', 'time'
        ]
    
        # Check if question is a dictionary
        if not isinstance(question, dict):
            errors.append(f"Question {index + 1}: Must be a dictionary, got {type(question).__name__}")
            return errors
    
        if not question.get('question') or not question.get('question').strip():
            errors.append(f"Question {index + 1}: Question text is required")
    
        if not question.get('type') or question.get('type') not in question_types:
            errors.append(f"Question {index + 1}: Invalid question type")
    
        # Validate options for choice-based questions
        if question.get('type') in ['multiple-choice', 'checkboxes', 'dropdown']:
            options = question.get('options', [])
            if not isinstance(options, list):
                errors.append(f"Question {index + 1}: Options must be a list")
            elif not options or len(options) == 0:
                errors.append(f"Question {index + 1}: At least one option is required")
            else:
                # Check for empty options
                for j, option in enumerate(options):
                    if not option or not str(option).strip():
                        errors.append(f"Question {index + 1}, Option {j + 1}: Option text cannot be empty")
    
        return errors
    
    def __str__(self):
        return f'<Form {self.title}>'

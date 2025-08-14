from mongoengine import Document, IntField, EmbeddedDocument,EmbeddedDocumentListField,StringField, ListField, BooleanField, DateTimeField, DictField, ReferenceField
from datetime import datetime
from app.models.media import Media
from app.models.service import Service

class Question(EmbeddedDocument):
    id = IntField()  # or UUID / ObjectId string
    type = StringField(required=True)  # e.g., "text", "image", etc.
    question = StringField(required=True)
    options = ListField(StringField())
    required = BooleanField(default=False)
    hasOther = BooleanField(default=False)
    scaleMin = IntField()
    scaleMax = IntField()
    minLabel = StringField()
    maxLabel = StringField()
    media = ReferenceField(Media)


class Form(Document):
    title = StringField(required=True, max_length=255)
    description = StringField()
    service = ReferenceField(Service, required=True)
    #questions = ListField(DictField()) # Changed to store dictionaries for each question
    questions = EmbeddedDocumentListField(Question)
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
    
    def _question_to_dict(self, question):
        return {
            "id": question.id,
            "type": question.type,
            "question": question.question,
            "options": question.options,
            "required": question.required,
            "hasOther": question.hasOther,
            "scaleMin": question.scaleMin,
            "scaleMax": question.scaleMax,
            "minLabel": getattr(question, "minLabel", ""),
            "maxLabel": getattr(question, "maxLabel", ""),
            "media": {
                "id": str(question.media.id),
                "url": getattr(question.media, "url", "")  # optional
        } if question.media else None
    }

    def to_dict(self):
        """Convert Form object to dictionary for MongoDB storage"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "service_id": str(self.service.id) if self.service else None,
            # "questions": self.questions,
            "questions": [self._question_to_dict(q) for q in self.questions],
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
        """Validate individual question (now a Question object)"""
        errors = []
        question_types = [
            'multiple-choice', 'checkboxes', 'dropdown',
            'short-answer', 'paragraph', 'linear-scale',
            'date', 'time'
        ]

        # Check type
        if not isinstance(question, Question):
            errors.append(f"Question {index + 1}: Must be a Question object, got {type(question).__name__}")
            return errors

        # Question text
        if not question.question or not question.question.strip():
            errors.append(f"Question {index + 1}: Question text is required")

        # Question type
        if not question.type or question.type not in question_types:
            errors.append(f"Question {index + 1}: Invalid question type")

        # Options for choice-based questions
        if question.type in ['multiple-choice', 'checkboxes', 'dropdown']:
            options = question.options
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
    


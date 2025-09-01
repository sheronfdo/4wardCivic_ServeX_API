from mongoengine import Document, IntField, EmbeddedDocument,EmbeddedDocumentListField,StringField, ListField, BooleanField, DateTimeField, DictField, ReferenceField
from datetime import datetime
from app.models.media import Media
from app.models.service import Service
import os

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

    fileUploadType = StringField(default='any')  # 'images', 'pdf', 'audio', 'video', 'documents', 'custom', 'any'
    maxFileSize = IntField(default=10)  # in MB
    customFileTypes = StringField(default='')  


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
        } if question.media else None,
            "fileUploadType": question.fileUploadType,
            "maxFileSize": question.maxFileSize,
            "customFileTypes": question.customFileTypes
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
            'date', 'time','file-upload',
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

        if question.type == 'file-upload':
            # Validate file upload type
            valid_upload_types = ['any', 'images', 'pdf', 'audio', 'video', 'documents', 
                                'spreadsheets', 'presentations', 'archives', 'custom']
            if question.fileUploadType not in valid_upload_types:
                errors.append(f'Invalid fileUploadType for question {question.id}: {question.fileUploadType}')
            
            # Validate max file size
            if not isinstance(question.maxFileSize, int) or question.maxFileSize <= 0 or question.maxFileSize > 100:
                errors.append(f'Invalid maxFileSize for question {question.id}: must be between 1-100 MB')
            
            # Validate custom file types if type is custom
            if question.fileUploadType == 'custom':
                if not question.customFileTypes or not question.customFileTypes.strip():
                    errors.append(f'Custom file types required for question {question.id} when fileUploadType is "custom"')
                elif question.customFileTypes:
                    # Validate format of custom file types
                    custom_types = [t.strip() for t in question.customFileTypes.split(',')]
                    for file_type in custom_types:
                        if not file_type.startswith('.'):
                            errors.append(f'Invalid custom file type format for question {question.id}: "{file_type}" should start with "."')

        return errors

    def get_allowed_extensions(file_upload_type, custom_file_types=''):
        """Get allowed file extensions based on upload type"""
        file_type_map = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'pdf': ['.pdf'],
            'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'],
            'documents': ['.doc', '.docx', '.txt', '.rtf', '.odt'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'any': []  # Empty list means any file type
        }
        
        if file_upload_type == 'custom' and custom_file_types:
            return [ext.strip() for ext in custom_file_types.split(',') if ext.strip()]
        
        return file_type_map.get(file_upload_type, [])
    
    def validate_uploaded_file(file, question):
        """Validate uploaded file against question constraints"""
        errors = []
        
        if question.type != 'file-upload':
            return errors
        
        # Check file size
        file_size_mb = len(file.read()) / (1024 * 1024)
        file.seek(0)  # Reset file pointer
        
        if file_size_mb > question.maxFileSize:
            errors.append(f'File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({question.maxFileSize}MB)')
        
        # Check file type
        if question.fileUploadType != 'any':
            allowed_extensions = get_allowed_extensions(question.fileUploadType, question.customFileTypes)
            if allowed_extensions:
                file_extension = os.path.splitext(file.filename)[1].lower()
                if file_extension not in [ext.lower() for ext in allowed_extensions]:
                    errors.append(f'File type "{file_extension}" is not allowed. Allowed types: {", ".join(allowed_extensions)}')
        
        return errors
    def __str__(self):
        return f'<Form {self.title}>'
    


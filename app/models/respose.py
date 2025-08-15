from mongoengine import Document, ReferenceField, StringField, DateTimeField, DictField
from datetime import datetime
from app.models.form import Form
from app.models.user import User
from app.models.service_requested import ServiceRequested
from app.models.status import STATUS
class FormResponse(Document):
    form = ReferenceField(Form, required=True)
    user = ReferenceField(User, required=True)
    service_requested = ReferenceField('ServiceRequested',required=False)  # Optional, if linked to a service request
    responses = DictField()# question_id -> answer
    submitted_at = DateTimeField(default=datetime.utcnow)
    status = StringField(required=True, choices=STATUS)
    # respondent_email = StringField()
    # ip_address = StringField()
    # user_agent = StringField()
    # submitted_at = DateTimeField()

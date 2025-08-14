from mongoengine import Document, ReferenceField, StringField, DateTimeField, DictField
from app.models.form import Form

class FormResponse(Document):
    form = ReferenceField(Form, required=True)
    responses = DictField()  # question_id -> answer
    respondent_email = StringField()
    ip_address = StringField()
    user_agent = StringField()
    submitted_at = DateTimeField()

from bson import ObjectId
from datetime import datetime
import os
from app.models.form import Form 
from app.models.form import Question
from app.models.service import Service
from app.models.media import Media
from app.models.respose import FormResponse
from app.models.user import User
from app.models.service_requested import ServiceRequested
from typing import List, Optional, Dict, Any

class FormService:
    
    @staticmethod
    def create_form(form_data, created_by=None):
        """Create a new form"""
        try:
            # Ensure questions is a list
            questions = form_data.get('questions', [])
            if not isinstance(questions, list):
                return {
                    'success': False,
                    'message': 'Questions must be a list'
                }

            # Get and validate service
            service_id = form_data.get('serviceId')
            if not service_id or not ObjectId.is_valid(service_id):
                return {
                    'success': False,
                    'message': 'Valid serviceId is required'
                }

            service = Service.objects(id=service_id).first()
            if not service:
                return {
                    'success': False,
                    'message': 'Service not found'
                }

            # Process questions to link media
            processed_questions = []
            for q in form_data.get('questions', []):
                media_obj = None
                if q.get('mediaId') and ObjectId.is_valid(q['mediaId']):
                    media_obj = Media.objects(id=q['mediaId']).first()
                processed_questions.append(
                    Question(
                        id=q.get('id'),
                        type=q.get('type'),
                        question=q.get('question'),
                        options=q.get('options', []),
                        required=q.get('required', False),
                        hasOther=q.get('hasOther', False),
                        scaleMin=q.get('scaleMin'),
                        scaleMax=q.get('scaleMax'),
                        minLabel=q.get('minLabel'),
                        maxLabel=q.get('maxLabel'),
                        media=media_obj,
                        fileUploadType=q.get('fileUploadType', 'any'),
                        maxFileSize=q.get('maxFileSize', 10),
                        customFileTypes=q.get('customFileTypes', '')
                    )
                )

            form = Form(
                title=form_data.get('title'),
                description=form_data.get('description'),
                service=service,
                questions=processed_questions,
                created_by=created_by
            )
        
            # Validate form data
            validation_errors = form.validate_form_data()
            if validation_errors:
                return {
                    'success': False,
                    'message': 'Validation failed',
                    'errors': validation_errors
                }
        
            # Save to database
            form.save()
            return {
                'success': True,
                'message': 'Form created successfully',
                'form_id': str(form.id),
                'form': form.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating form: {str(e)}'
            }
        
    

    @staticmethod
    def get_form_by_id(form_id):
        """Get form by ID"""
        try:
            form = Form.objects.get(id=form_id)
            return {
                'success': True,
                'form': form.to_dict()
            }
        except Form.DoesNotExist:
            return {
                'success': False,
                'message': 'Form not found'
            }
        except Exception as e:
            return {
            'success': False,
            'message': f'Error retrieving form: {str(e)}'
        }
    
    @staticmethod
    def update_form(form_id, form_data, updated_by=None):
        """Update existing form"""
        try:
            # Check if form exists
            form = Form.objects.get(id=form_id)
        
            # Create updated form object for validation
            updated_form = Form(
                title=form_data.get('title', form.title),
                description=form_data.get('description', form.description),
                questions=form_data.get('questions', form.questions),
                created_by=form.created_by
            )
        
            # Validate form data
            validation_errors = updated_form.validate_form_data()
            if validation_errors:
                return {
                'success': False,
                'message': 'Validation failed',
                'errors': validation_errors
                }
        
            # Update form fields
            form.title = form_data.get('title', form.title)
            form.description = form_data.get('description', form.description)
            form.questions = form_data.get('questions', form.questions)
            form.updated_at = datetime.utcnow()
        
            # Save updated form
            form.save()
            return {
                'success': True,
                'message': 'Form updated successfully'
            }
        
        except Form.DoesNotExist:
            return {
                'success': False,
                'message': 'Form not found'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating form: {str(e)}'
            }
    
    @staticmethod
    def delete_form(form_id, deleted_by=None):
        """Delete form (soft delete by setting is_active to False)"""
        try:
            form = Form.objects.get(id=form_id)
            form.is_active = False
            form.updated_at = datetime.utcnow()
            form.save()
            return {
                'success': True,
                'message': 'Form deleted successfully'
            }
        except Form.DoesNotExist:
            return {
            'success': False,
            'message': 'Form not found'
        }
        except Exception as e:
            return {
                'success': False,
            }
    @staticmethod
    def submit_form_response(form_id: str, user_id: str,responses: dict,) -> dict:
        """Store user responses for a form"""
        try:

            form = Form.objects.get(id=form_id)
            user = User.objects.get(id=user_id)
            #service_requested = ServiceRequested.objects.get(id=None)
        except Form.DoesNotExist:
            return {'success': False, 'message': 'Form not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error retrieving form: {str(e)}'}

        try:
            # Create FormResponse object
            form_response = FormResponse(
                form=form,
                user=user,
                responses=responses,
                status='PENDING',
                submitted_at=datetime.utcnow()
            )
            form_response.save()
            return {'success': True, 'message': 'Response submitted successfully','form_respose_id':str(form_response.id)}
        except Exception as e:
            return {'success': False, 'message': f'Error saving response: {str(e)}'}
        
    @staticmethod
    def get_service_by_form_id(form_id: str) -> dict:
        """Get the service related to a form using form_id"""
        try:
            form = Form.objects.get(id=form_id)

            if not form.service:
                return {
                    'success': False,
                    'message': 'No service linked to this form'
                }

            return {
                'success': True,
                'service': form.service.to_dict() if hasattr(form.service, "to_dict") else form.service
            }

        except Form.DoesNotExist:
            return {
                'success': False,
                'message': 'Form not found'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving service: {str(e)}'
        }

   
from bson import ObjectId
from datetime import datetime
import os
from app.models.form import Form


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

            # Create Form object
            form = Form(
                title=form_data.get('title'),
                description=form_data.get('description'),
                questions=questions,
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
            form.save()  # MongoEngine's save method
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
    
   
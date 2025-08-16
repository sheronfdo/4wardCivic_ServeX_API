from bson import ObjectId
from datetime import datetime
from app.models.service import Service
from typing import List, Optional, Dict, Any
from app.models.service_requested import ServiceRequested
from app.models.user import User
from app.models.respose import FormResponse
from datetime import datetime, time

class ServiceRequestedService:
    
    @staticmethod
    def create_rqested_service(service_requested_data):
        """Create a new service request"""
        try:
            # Get and validate service
            service_id = service_requested_data.get('serviceId')
            user_id = service_requested_data.get('user_id')
            form_responses_Ids = service_requested_data.get('form_responses_ids', [])
            appointment_date_only= None
            try:
                datetime_obj = datetime.strptime(service_requested_data.get('appoiment_Date'), "%Y-%m-%dT%H:%M:%SZ")
                appointment_date_only =datetime_obj.date()
            except Exception as e:
                print(e)

            # Combine the date with time to create full datetime objects
            start_time = datetime.combine(appointment_date_only, datetime.strptime(service_requested_data.get("slot_start_time"), "%H:%M").time())
            end_time = datetime.combine(appointment_date_only, datetime.strptime(service_requested_data.get("slot_end_time"), "%H:%M").time())
            # Validate if ObjectId is correct
            if not service_id or not ObjectId.is_valid(service_id):
                return {
                    'success': False,
                    'message': 'Valid serviceId is required'
                }

            service = Service.objects(id=ObjectId(service_id)).first()
            if not service:
                return {
                    'success': False,
                    'message': 'Service not found'
                }
            
            user = User.objects(id=ObjectId(user_id)).first()
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }

            # Create a new service request object
            service_requested = ServiceRequested(
                user=user,
                service=service,
                appoiment_Date=appointment_date_only,
                slot_start_time=start_time,
                slot_end_time=end_time,
                status=service_requested_data.get('status', 'ACTIVE'),
            )
        
            # Validate form data using validate_service_requested_data() from the model
            validation_errors = service_requested.validate_service_requested_data()
            if validation_errors:
                return {
                    'success': False,
                    'message': 'Validation failed',
                    'errors': validation_errors
                }

            # Save to database
            service_requested.save()
            process_form_response(form_responses_Ids, service_requested)
            return {
                'success': True,
                'message': 'Service requested successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating service request: {str(e)}'
            }
        
    @staticmethod
    def get_all_requested_services(user_id=None, user_role=None):
        """Get all requested services with their form responses"""
        try:
            # Build query based on user role
            if user_role == 'Citizen':
                # Citizens can only see their own requests
                if not user_id:
                    return {
                        'success': False,
                        'message': 'User ID is required for citizens'
                    }
                query = {'user': ObjectId(user_id)}
            else:
                # GovAdmin can see all requests
                query = {}
            
            # Get all service requests
            service_requests = ServiceRequested.objects(**query).select_related()
            
            requested_services_data = []
            
            for service_request in service_requests:
                # Get form responses linked to this service request
                form_responses = FormResponse.objects(service_requested=service_request.id)
                
                # Format form responses data
                form_responses_data = []
                for form_response in form_responses:
                    form_responses_data.append({
                        'id': str(form_response.id),
                        'form_id': str(form_response.form.id) if form_response.form else None,
                        'form_title': form_response.form.title if form_response.form else None,
                        'responses': form_response.responses if hasattr(form_response, 'responses') else {},
                        'status': form_response.status if hasattr(form_response, 'status') else 'UNKNOWN',
                        'created_at': form_response.created_at.isoformat() if hasattr(form_response, 'created_at') else None,
                        'updated_at': form_response.updated_at.isoformat() if hasattr(form_response, 'updated_at') else None
                    })
                
                # Format service request data
                service_data = {
                    'id': str(service_request.id),
                    'user': {
                        'id': str(service_request.user.id),
                        'name': service_request.user.name if hasattr(service_request.user, 'name') else 'Unknown',
                        'email': service_request.user.email if hasattr(service_request.user, 'email') else 'Unknown'
                    },
                    'service': {
                        'id': str(service_request.service.id),
                        'title': service_request.service.title if hasattr(service_request.service, 'title') else 'Unknown',
                        'description': service_request.service.description if hasattr(service_request.service, 'description') else ''
                    },
                    'appointment_date': service_request.appoiment_Date.isoformat() if service_request.appoiment_Date else None,
                    'slot_start_time': service_request.slot_start_time.isoformat() if service_request.slot_start_time else None,
                    'slot_end_time': service_request.slot_end_time.isoformat() if service_request.slot_end_time else None,
                    'status': service_request.status,
                    'form_responses': form_responses_data,
                    'form_responses_count': len(form_responses_data),
                    'created_at': service_request.created_at.isoformat() if hasattr(service_request, 'created_at') else None,
                    'updated_at': service_request.updated_at.isoformat() if hasattr(service_request, 'updated_at') else None
                }
                
                requested_services_data.append(service_data)
            
            return {
                'success': True,
                'data': requested_services_data,
                'count': len(requested_services_data),
                'message': f'Retrieved {len(requested_services_data)} requested services'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving requested services: {str(e)}'    
            }
        
def process_form_response(form_responses_Ids: List[str], serviceRequestedId):
    """Update form responses to link them to the service request"""
    try:
        for form_response_id in form_responses_Ids:
            # Fetch the FormResponse using the ID
            form_response = FormResponse.objects(id=form_response_id).first()
            if form_response:
                form_response.service_requested=serviceRequestedId
                form_response.status="ACTIVE"
                form_response.save()
                # If found, update the FormResponse with the new serviceRequestedId
                  # Assuming `service_requested_id` is the field in FormResponse
        print("ok")
        # return {
        #     'success': True,
        #     'message': 'Form responses processed and linked successfully'
        # }

    except Exception as e:
        print(e)
        # return {
        #     'success': False,
        #     'message': f'Error processing form responses: {str(e)}'
        # }

                 

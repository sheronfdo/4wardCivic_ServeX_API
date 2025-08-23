from bson import ObjectId
from datetime import datetime
from app.models.service import Service
from typing import List, Optional, Dict, Any
from app.models.service_requested import ServiceRequested
from app.models.user import User
from app.models.respose import FormResponse
from datetime import datetime, time
from app.models.authority import Authority 
from bson.errors import InvalidId
from collections import defaultdict
from datetime import timedelta

class ServiceRequestedService:
    
    @staticmethod
    def create_rqested_service(service_requested_data):
        """Create a new service request"""
        try:
            # Get and validate service
            service_id = service_requested_data.get('serviceId')
            user_id = service_requested_data.get('user_id')

            slot_start_time = service_requested_data.get("slot_start_time") 
            slot_end_time = service_requested_data.get("slot_end_time")
            
            form_responses_Ids = service_requested_data.get('form_responses_ids', [])
            appointment_date_only= None
            try:
                datetime_obj = datetime.strptime(service_requested_data.get('appoiment_Date'), "%Y-%m-%dT%H:%M:%SZ")
                appointment_date_only =datetime_obj.date()
            except Exception as e:
                print(e)
            if slot_start_time and slot_end_time:
    
                start_time = datetime.combine(appointment_date_only, 
                                datetime.strptime(slot_start_time, "%H:%M").time())
                end_time = datetime.combine(appointment_date_only, 
                              datetime.strptime(slot_end_time, "%H:%M").time())
            else:
                # Handle case when optional fields are not provided
                start_time = None
                end_time = None
           
            # Combine the date with time to create full datetime objects
            #start_time = datetime.combine(appointment_date_only, datetime.strptime(service_requested_data.get("slot_start_time"), "%H:%M").time())
            #end_time = datetime.combine(appointment_date_only, datetime.strptime(service_requested_data.get("slot_end_time"), "%H:%M").time())
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

            authority_id = service.authority.id
            authority = Authority.objects(id=ObjectId(authority_id)).first()
            if not authority:
                    return {
                    'success': False,
                    'message': 'Authority not found'
                }

            # Create a new service request object
            service_requested = ServiceRequested(
                user=user,
                service=service,
                authority=authority,
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
    def get_all_requested_services(user_id=None, authority_id=None):
        """Get all requested services with their form responses, filtered by user or authority."""
        try:
            # Build query based on user role or authority
            if authority_id and authority_id != 'None':
                # Authority can see all requests tied to their authority
                query = {'authority': ObjectId(authority_id)}  # Correct field name 'authority'
            elif user_id:
                # Citizens can only see their own requests
                query = {'user': ObjectId(user_id)}
            else:
                # If neither authority_id nor user_id is provided, return error
                return {
                    'success': False,
                    'message': 'Either user_id or authority_id is required'
                }

            # Get all service requests based on the filtered query
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
                
                # Fetch service details using service ID reference
                service = Service.objects(id=service_request.service.id).first() if service_request.service else None
                
                # Format service data
                service_data = {
                    'id': str(service_request.id),
                    'user': {
                        'id': str(service_request.user.id),
                        'name': service_request.user.name if hasattr(service_request.user, 'name') else 'Unknown',
                        'email': service_request.user.email if hasattr(service_request.user, 'email') else 'Unknown'
                    },
                    'service': {
                        'id': str(service.id) if service else 'Unknown',
                        'service_name': service.service_name if service else 'Unknown',
                        'note': service.note if service else 'No note available'
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
    
    @staticmethod
    def get_requested_services_count(user_id=None, authority_id=None):
        """Get count of requested services and form responses, filtered by user or authority."""
        try:
            # Build query based on user role or authority
            if authority_id and authority_id != 'None':
                query = {'authority': ObjectId(authority_id)}
            elif user_id:
                query = {'user': ObjectId(user_id)}
            else:
                return {
                    'success': False,
                    'message': 'Either user_id or authority_id is required'
                }

            # Get all service requests based on filter
            service_requests = ServiceRequested.objects(**query)

            # Count service requests
            service_requests_count = service_requests.count()

            # Count all form responses linked to those service requests
            form_responses_count = FormResponse.objects(
                service_requested__in=[req.id for req in service_requests]
            ).count()

            return {
                'success': True,
                'service_requests_count': service_requests_count,
                'form_responses_count': form_responses_count,
                'message': f"Retrieved counts for {service_requests_count} service requests with {form_responses_count} form responses"
            }

        except Exception as e:
            return {
                'success': False,
                'message': f"Error retrieving counts: {str(e)}"
            }

    @staticmethod
    def get_peak_booking_hours():
        try:
            # Fetch all appointments (you can add filters for specific dates if needed)
            all_appointments = ServiceRequested.objects.all()

            # Dictionary to store the count of appointments for each hour
            booking_counts = defaultdict(int)
            
            for appointment in all_appointments:
                start_time = appointment.slot_start_time
                end_time = appointment.slot_end_time
                
                # Iterate over each hour in the time range
                current_time = start_time
                while current_time < end_time:
                    # Count the appointment in this hour
                    booking_counts[current_time.hour] += 1
                    current_time += timedelta(hours=1)

            # Sort by the number of bookings per hour in descending order
            sorted_booking_counts = sorted(booking_counts.items(), key=lambda x: x[1], reverse=True)

            # Get the top 5 peak hours
            peak_hours = sorted_booking_counts[:5]

            return {
                'success': True,
                'peak_hours': peak_hours,
                'message': 'Successfully calculated peak booking hours'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error calculating peak booking hours: {str(e)}'
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

                 

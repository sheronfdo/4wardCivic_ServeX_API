from bson import ObjectId
from datetime import datetime
from app.models.user import User
from app.models.authority import Authority 
from app.models.staff_roll import StaffRoll  # Fixed import name

class StaffRollService:
    
    @staticmethod
    def create_roll_for_staff(authority_id, roll_data):
        """Create a new roll for staff"""
        try:
            # Get authority by ID
            authority = Authority.objects(id=ObjectId(authority_id)).first()
            if not authority:
                return {
                    'success': False,
                    'message': 'Authority not found'
                }

            # Extract roll name from roll_data
            if isinstance(roll_data, dict):
                roll_name = roll_data.get('name') or roll_data.get('staffroll')
            else:
                roll_name = str(roll_data)
            
            if not roll_name or not roll_name.strip():
                return {
                    'success': False,
                    'message': 'Roll name is required'
                }

            # Check if staff roll with same name already exists for this authority
            existing_roll = StaffRoll.objects(
                staffroll=roll_name.strip(),
                authority=authority
            ).first()
            
            if existing_roll:
                return {
                    'success': False,
                    'message': 'Staff roll with this name already exists for this authority'
                }

            # Create a new staff roll object
            staff_roll = StaffRoll(
                staffroll=roll_name.strip(),
                authority=authority,
                status='ACTIVE'  # Fixed status assignment
            )
        
            # Validate form data
            validation_errors = staff_roll.validate_staff_roll()
            if validation_errors:
                return {
                    'success': False,
                    'message': 'Validation failed',
                    'errors': validation_errors
                }

            # Save to database
            staff_roll.save()
            
            print(f"Staff roll saved successfully: {staff_roll.id}")  # Debug log
        
            return {
                'success': True,
                'message': 'Roll added successfully',
                'data': staff_roll.to_dict()
            }
        
        except Exception as e:
            print(f"Error in create_roll_for_staff: {str(e)}")  # Debug log
            return {
                'success': False,
                'message': f'Error creating roll: {str(e)}'
            }
    
    @staticmethod
    def get_rolls_by_authority(authority_id):
        """Get all rolls for a specific authority"""
        try:
            authority = Authority.objects(id=ObjectId(authority_id)).first()
            if not authority:
                return {
                    'success': False,
                    'message': 'Authority not found'
                }
            
            rolls = StaffRoll.objects(authority=authority, status='ACTIVE').order_by('-created_at')
            rolls_data = [roll.to_dict() for roll in rolls]
            
            return {
                'success': True,
                'data': rolls_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching rolls: {str(e)}'
            }
        
    @staticmethod
    def get_authority_staff_list(authority_id):
        """Get all staff members for a specific authority"""
        try:
            # Validate authority exists
            authority_obj = Authority.objects(id=ObjectId(authority_id)).first()
            if not authority_obj:
                return {
                    'success': False,
                    'message': 'Authority not found'
                }
            
            # Get all staff members for this authority
            staff_members = User.objects(
                authority=authority_obj,
                role='GovStaff'
            ).order_by('-created_at')
            
            # Convert to list with detailed information
            staff_list = []
            for staff in staff_members:
                staff_data = {
                    'id': str(staff.id),
                    'fullname': staff.fullname,
                    'name': staff.name,
                    'email': staff.email,
                    'phone_number': staff.phone_number,
                    'status': staff.status,
                    'is_active': staff.is_active,
                    'last_login': staff.last_login.strftime('%Y-%m-%d %H:%M:%S') if staff.last_login else None,
                    'staff_role': {
                        'id': str(staff.staffrole.id) if staff.staffrole else None,
                        'staffroll': staff.staffrole.staffroll if staff.staffrole else None,
                    } if staff.staffrole else None
                }
                staff_list.append(staff_data)
            
            
            return {
                'success': True,
                'data': staff_list,
                'total_count': len(staff_list),
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving staff list: {str(e)}'
            }
    
    @staticmethod
    def get_staff_list_by_roll(role_id):
        """Get all staff members for a specific roll"""
        try:
            # Validate if the staff role exists by ObjectId
            staff_members = User.objects(staffrole=ObjectId(role_id), role='GovStaff').order_by('-created_at')
            
            # Check if any staff members exist
            if not staff_members:
                return {
                    'success': False,
                    'message': 'No staff members found for the given roll'
                }
            
            # Convert to list with detailed information
            staff_list = []
            for staff in staff_members:
                staff_data = {
                    'id': str(staff.id),
                    'name': staff.name,  # Staff name
                }
                staff_list.append(staff_data)
            
            return {
                'success': True,
                'data': staff_list,
                'total_count': len(staff_list),
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving staff list: {str(e)}'
            }

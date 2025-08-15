"""
User service for business logic operations
"""
from typing import Optional, Dict, List, Any
from datetime import datetime
from mongoengine import ValidationError, NotUniqueError
from mongoengine.queryset.visitor import Q

from app.models import Authority
from app.models.user import User
from app.utils.email import send_verification_email
from app.utils.validators import validate_email, validate_password, validate_user_data
import uuid
from bson.errors import InvalidId


class UserService:
    """Service class for user-related business logic"""

    def create_authority_user(data):
        """Create Government authority user"""
        try:
            if not data.get('authority'):
                return {'success': False, 'message': 'Admin role requires an authority'}

            if User.objects(email=data['email'].lower().strip()).first():
                raise ValueError('Email already registered')

            authority_obj = Authority.objects.get(id=data['authority'])
            token = None
            if data['email'].lower().strip() != authority_obj.email:
                token = str(uuid.uuid4())
            user = User(
                name=data.get('name', 'Authority Admin'),
                email=data['email'].lower().strip(),
                role=data.get('role', 'GovAdmin'),
                authority=authority_obj,
                verification_token=token,
                is_verified=(data['email'].lower().strip() == authority_obj.email),
                status="PENDING"
            )
            user.set_password(data['password'])

            if user.is_verified:
                user.is_verified = True
                user.verification_token = None
                user.status = "ACTIVE"
                authority = Authority.objects(id=data['authority']).first()
                if not authority:
                    raise ValueError('Authority not found')
                authority.status = "ACTIVE"
                authority.save()

            user.save()
            if token:
                send_verification_email(data['email'], data['name'], token, is_authority=False)
            return {'success': True, 'data': {'id': str(user.id), 'email': user.email}, 'is_verified': user.is_verified}
        except ValidationError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            return {'success': False, 'message': f'Unexpected error: {str(e)}'}

    def verify_admin_email(token):
        user = User.objects(verification_token=token, is_verified=False).first()
        if not user:
            raise ValueError('Invalid or expired token')
        user.is_verified = True
        user.verification_token = None
        user.status = "ACTIVE"
        user.save()
        response = {
            'authority_id': str(user.authority.id) if user.authority else None,
            'user_id': str(user.id)
        }
        return response

    def create_citizen_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create citizen user"""
        try:
            if User.objects(email=data['email'].lower().strip()).first():
                raise ValueError('Email already registered')

            user = User(
                name=data.get('name', 'Authority Admin'),
                email=data['email'].lower().strip(),
                role=data.get('role', 'Citizen'),
                authority=None,
                is_verified=True,
                status="ACTIVE"
            )
            user.save()

            return {'success': True, 'data': {'id': str(user.id), 'email': user.email}}
        except ValidationError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            return {'success': False, 'message': f'Unexpected error: {str(e)}'}

    def citizen_registration_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create citizen registration"""
        try:
            user = User.objects(id=data['citizen_id']).first()
            if not user:
                raise ValueError('User Not Found!')

            user.fullname = data.get('fullname')
            user.id_type = data.get('id_type')
            user.id_number = data.get('id_number')
            user.phone_number = data.get('phone_number')
            user.save()

            return {'success': True, 'data': {'id': str(user.id), 'email': user.email}}
        except ValidationError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            return {'success': False, 'message': f'Unexpected error: {str(e)}'}


    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Dictionary with success status and user data or error message
        """
        try:
            # Validate input data
            validation_result = validate_user_data(user_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message']
                }

            # Check if user already exists
            if self.find_by_email(user_data['email']):
                return {
                    'success': False,
                    'message': 'User with this email already exists'
                }

            # Create new user
            user = User(
                name=user_data['name'],
                email=user_data['email'].lower().strip(),
                role=user_data.get('role', 'User')
            )
            user.set_password(user_data['password'])
            user.save()

            return {
                'success': True,
                'message': 'User created successfully',
                'data': user.to_dict()
            }

        except NotUniqueError:
            return {
                'success': False,
                'message': 'User with this email already exists'
            }
        except ValidationError as e:
            return {
                'success': False,
                'message': f'Validation error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating user: {str(e)}'
            }

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID string
            
        Returns:
            User object or None if not found
        """
        try:
            return User.objects(id=user_id).first()
        except Exception:
            return None

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        try:
            return User.objects(email=email.lower().strip(), status="ACTIVE").first()
        except Exception:
            return None

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dictionary with authentication result
        """
        try:
            user = self.find_by_email(email)
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }

            if not user.check_password(password):
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }

            if not user.is_active:
                return {
                    'success': False,
                    'message': 'Account is deactivated'
                }

            # Update last login
            user.update_last_login()

            return {
                'success': True,
                'message': 'Authentication successful',
                'data': user.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Authentication error: {str(e)}'
            }

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            user_id: User ID to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Dictionary with update result
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }

            # Allowed fields to update
            allowed_fields = ['name', 'email', 'role', 'is_active']

            # Validate and update fields
            for field, value in update_data.items():
                if field in allowed_fields:
                    if field == 'email':
                        # Check if email is already taken by another user
                        existing_user = User.objects(
                            email=value.lower().strip(),
                            id__ne=user.id
                        ).first()
                        if existing_user:
                            return {
                                'success': False,
                                'message': 'Email is already taken by another user'
                            }
                        user.email = value.lower().strip()
                    elif field == 'role':
                        if value not in User.ROLE_CHOICES:
                            return {
                                'success': False,
                                'message': f'Invalid role. Must be one of: {User.ROLE_CHOICES}'
                            }
                        user.role = value
                    else:
                        setattr(user, field, value)

            user.updated_at = datetime.utcnow()
            user.save()

            return {
                'success': True,
                'message': 'User updated successfully',
                'data': user.to_dict()
            }

        except ValidationError as e:
            return {
                'success': False,
                'message': f'Validation error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating user: {str(e)}'
            }

    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """
        Delete user by ID
        
        Args:
            user_id: User ID to delete
            
        Returns:
            Dictionary with deletion result
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }

            user.delete()

            return {
                'success': True,
                'message': 'User deleted successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting user: {str(e)}'
            }

    def get_all_users(self, page: int = 1, limit: int = 10, search: str = None, role: str = None) -> Dict[str, Any]:
        """
        Get paginated list of users with optional filtering
        
        Args:
            page: Page number (starting from 1)
            limit: Number of users per page
            search: Search term for name or email
            role: Filter by user role
            
        Returns:
            Dictionary with users list and pagination info
        """
        try:
            # Build query
            query = User.objects()

            # Apply filters
            if search:
                query = query.filter(
                    Q(name__icontains=search) | Q(email__icontains=search)
                )

            if role and role in User.ROLE_CHOICES:
                query = query.filter(role=role)

            # Calculate pagination
            total = query.count()
            skip = (page - 1) * limit
            users = query.skip(skip).limit(limit)

            # Convert to dictionaries
            users_data = [user.to_dict() for user in users]

            return {
                'success': True,
                'data': {
                    'users': users_data,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total,
                        'pages': (total + limit - 1) // limit
                    }
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving users: {str(e)}'
            }

    def change_password(self, user_id: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            Dictionary with password change result
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }

            # Verify current password
            if not user.check_password(current_password):
                return {
                    'success': False,
                    'message': 'Current password is incorrect'
                }

            # Validate new password
            password_validation = validate_password(new_password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'message': password_validation['message']
                }

            # Update password
            user.set_password(new_password)
            user.updated_at = datetime.utcnow()
            user.save()

            return {
                'success': True,
                'message': 'Password changed successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error changing password: {str(e)}'
            }

    def toggle_user_status(self, user_id: str) -> Dict[str, Any]:
        """
        Toggle user active status
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with toggle result
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }

            user.is_active = not user.is_active
            user.updated_at = datetime.utcnow()
            user.save()

            status = 'activated' if user.is_active else 'deactivated'
            return {
                'success': True,
                'message': f'User {status} successfully',
                'data': user.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating user status: {str(e)}'
            }

    def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics
        
        Returns:
            Dictionary with user statistics
        """
        try:
            total_users = User.objects().count()
            active_users = User.objects(is_active=True).count()
            admin_users = User.objects(role='Admin').count()
            regular_users = User.objects(role='User').count()

            return {
                'success': True,
                'data': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'inactive_users': total_users - active_users,
                    'admin_users': admin_users,
                    'regular_users': regular_users
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving user stats: {str(e)}'
            }

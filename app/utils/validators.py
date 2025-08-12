"""
Input validation utilities
"""
import re
from typing import Dict, Any


def validate_email(email: str) -> Dict[str, Any]:
    """
    Validate email format
    
    Args:
        email: Email string to validate
        
    Returns:
        Dictionary with validation result
    """
    if not email:
        return {'valid': False, 'message': 'Email is required'}
    
    email = email.strip()
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return {'valid': False, 'message': 'Invalid email format'}
    
    if len(email) > 254:
        return {'valid': False, 'message': 'Email is too long'}
    
    return {'valid': True, 'message': 'Valid email'}


def validate_password(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    
    Args:
        password: Password string to validate
        
    Returns:
        Dictionary with validation result
    """
    if not password:
        return {'valid': False, 'message': 'Password is required'}
    
    if len(password) < 6:
        return {'valid': False, 'message': 'Password must be at least 6 characters long'}
    
    if len(password) > 128:
        return {'valid': False, 'message': 'Password is too long'}
    
    # Check for at least one letter and one number
    if not re.search(r'[A-Za-z]', password):
        return {'valid': False, 'message': 'Password must contain at least one letter'}
    
    if not re.search(r'[0-9]', password):
        return {'valid': False, 'message': 'Password must contain at least one number'}
    
    return {'valid': True, 'message': 'Valid password'}


def validate_name(name: str) -> Dict[str, Any]:
    """
    Validate name
    
    Args:
        name: Name string to validate
        
    Returns:
        Dictionary with validation result
    """
    if not name:
        return {'valid': False, 'message': 'Name is required'}
    
    name = name.strip()
    
    if len(name) < 2:
        return {'valid': False, 'message': 'Name must be at least 2 characters long'}
    
    if len(name) > 100:
        return {'valid': False, 'message': 'Name is too long'}
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return {'valid': False, 'message': 'Name can only contain letters, spaces, hyphens, and apostrophes'}
    
    return {'valid': True, 'message': 'Valid name'}


def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete user data for creation/update
    
    Args:
        user_data: Dictionary containing user data
        
    Returns:
        Dictionary with validation result
    """
    # Required fields for user creation
    required_fields = ['name', 'email', 'password']
    
    # Check for required fields
    for field in required_fields:
        if field not in user_data or not user_data[field]:
            return {'valid': False, 'message': f'{field.capitalize()} is required'}
    
    # Validate name
    name_validation = validate_name(user_data['name'])
    if not name_validation['valid']:
        return name_validation
    
    # Validate email
    email_validation = validate_email(user_data['email'])
    if not email_validation['valid']:
        return email_validation
    
    # Validate password
    password_validation = validate_password(user_data['password'])
    if not password_validation['valid']:
        return password_validation
    
    # Validate role if provided
    if 'role' in user_data and user_data['role']:
        valid_roles = ['Admin', 'User']
        if user_data['role'] not in valid_roles:
            return {'valid': False, 'message': f'Invalid role. Must be one of: {valid_roles}'}
    
    return {'valid': True, 'message': 'Valid user data'}


def validate_pagination_params(page: str, limit: str) -> Dict[str, Any]:
    """
    Validate pagination parameters
    
    Args:
        page: Page number as string
        limit: Limit number as string
        
    Returns:
        Dictionary with validation result and converted values
    """
    try:
        page_int = int(page) if page else 1
        limit_int = int(limit) if limit else 10
        
        if page_int < 1:
            return {'valid': False, 'message': 'Page must be greater than 0'}
        
        if limit_int < 1:
            return {'valid': False, 'message': 'Limit must be greater than 0'}
        
        if limit_int > 100:
            return {'valid': False, 'message': 'Limit cannot exceed 100'}
        
        return {
            'valid': True,
            'message': 'Valid pagination parameters',
            'page': page_int,
            'limit': limit_int
        }
        
    except ValueError:
        return {'valid': False, 'message': 'Page and limit must be valid integers'}


def validate_search_params(search: str) -> Dict[str, Any]:
    """
    Validate search parameters
    
    Args:
        search: Search term
        
    Returns:
        Dictionary with validation result
    """
    if not search:
        return {'valid': True, 'message': 'No search term provided', 'search': None}
    
    search = search.strip()
    
    if len(search) < 2:
        return {'valid': False, 'message': 'Search term must be at least 2 characters long'}
    
    if len(search) > 100:
        return {'valid': False, 'message': 'Search term is too long'}
    
    return {'valid': True, 'message': 'Valid search term', 'search': search}

def validate_file(file):
    """
    Validate uploaded file
    
    Args:
        file: FileStorage object
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    if not file or not hasattr(file, 'filename'):
        return False
    
    if file.filename == '':
        return False
    
    # Check file extension
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav'}
    
    if '.' not in file.filename:
        return False
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions

def validate_file_size(file, max_size_mb=16):
    """
    Validate file size
    
    Args:
        file: FileStorage object
        max_size_mb: Maximum file size in MB
        
    Returns:
        bool: True if file size is valid, False otherwise
    """
    if not file:
        return False
    
    # Get file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return size <= max_size_bytes

def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present and not empty
    
    Args:
        data: Dictionary with data to validate
        required_fields: List of required field names
        
    Returns:
        tuple: (is_valid, missing_fields)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == '':
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields
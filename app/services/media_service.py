import os
import uuid
from werkzeug.utils import secure_filename
from app.models.media import Media
from flask import current_app

class MediaService:
    
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav'}
    
    @classmethod
    def _ensure_upload_directory(cls):
        """Ensure upload directory exists"""
        if not os.path.exists(cls.UPLOAD_FOLDER):
            os.makedirs(cls.UPLOAD_FOLDER)
    
    @classmethod
    def _is_allowed_file(cls, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def upload_file(cls, file):
        """
        Upload and save media file
        
        Args:
            file: FileStorage object from Flask request
            
        Returns:
            dict: Result with success status and data/error
        """
        try:
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file provided'}
            
            if not cls._is_allowed_file(file.filename):
                return {'success': False, 'error': 'File type not allowed'}
            
            # Ensure upload directory exists
            cls._ensure_upload_directory()
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Save file
            file_path = os.path.join(cls.UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # Save to database
            media_item = Media(
                file_path=file_path,
                file_name=filename
            )
            media_item.save()
            
            return {
                'success': True,
                'data': {
                    'id': str(media_item.id),
                    'file_name': media_item.file_name,
                    'file_path': media_item.file_path,
                    'uploaded_at': media_item.uploaded_at.isoformat()
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_all_media(cls):
        """
        Get all media files from database
        
        Returns:
            dict: Result with success status and data/error
        """
        try:
            media_items = Media.objects()
            media_list = []
            
            for item in media_items:
                media_list.append({
                    'id': str(item.id),
                    'file_name': item.file_name,
                    'file_path': item.file_path,
                    'uploaded_at': item.uploaded_at.isoformat()
                })
            
            return {'success': True, 'data': media_list}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_media_by_id(cls, media_id):
        """
        Get specific media by ID
        
        Args:
            media_id (str): Media object ID
            
        Returns:
            dict: Result with success status and data/error
        """
        try:
            media_item = Media.objects(id=media_id).first()
            
            if not media_item:
                return {'success': False, 'error': 'Media not found'}
            
            return {
                'success': True,
                'data': {
                    'id': str(media_item.id),
                    'file_name': media_item.file_name,
                    'file_path': media_item.file_path,
                    'uploaded_at': media_item.uploaded_at.isoformat()
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def delete_media(cls, media_id):
        """
        Delete media by ID (both database record and file)
        
        Args:
            media_id (str): Media object ID
            
        Returns:
            dict: Result with success status and data/error
        """
        try:
            media_item = Media.objects(id=media_id).first()
            
            if not media_item:
                return {'success': False, 'error': 'Media not found'}
            
            # Delete file from filesystem
            if os.path.exists(media_item.file_path):
                os.remove(media_item.file_path)
            
            # Delete from database
            media_item.delete()
            
            return {'success': True, 'data': 'Media deleted successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
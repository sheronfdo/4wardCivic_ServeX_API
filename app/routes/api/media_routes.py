from flask import Blueprint, request, jsonify
from app.services.media_service import MediaService
from app.utils.validators import validate_file
import os

media_bp = Blueprint('media', __name__, url_prefix='/media')

@media_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a media file
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not validate_file(file):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Use service to handle upload
        result = MediaService.upload_file(file)
        
        if result['success']:
            return jsonify({
                'message': 'File uploaded successfully',
                'data': result['data']
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@media_bp.route('/', methods=['GET'])
def get_media():
    """
    Get all media files
    """
    try:
        result = MediaService.get_all_media()
        
        if result['success']:
            return jsonify({
                'message': 'Media retrieved successfully',
                'data': result['data']
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve media: {str(e)}'}), 500

@media_bp.route('/<media_id>', methods=['GET'])
def get_media_by_id(media_id):
    """
    Get specific media by ID
    """
    try:
        result = MediaService.get_media_by_id(media_id)
        
        if result['success']:
            return jsonify({
                'message': 'Media retrieved successfully',
                'data': result['data']
            }), 200
        else:
            return jsonify({'error': result['error']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve media: {str(e)}'}), 500

@media_bp.route('/<media_id>', methods=['DELETE'])
def delete_media(media_id):
    """
    Delete specific media by ID
    """
    try:
        result = MediaService.delete_media(media_id)
        
        if result['success']:
            return jsonify({
                'message': 'Media deleted successfully'
            }), 200
        else:
            return jsonify({'error': result['error']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete media: {str(e)}'}), 500
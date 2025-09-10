"""
Temporary Private Image Storage Service
Handles image uploads with automatic cleanup and private access
"""

import os
import uuid
import time
import json
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.files.base import ContentFile
import base64
import re

class TemporaryImageStorage:
    """
    Private temporary image storage with automatic cleanup
    Images are stored with unique UUIDs and expire after a set time
    """
    
    def __init__(self):
        self.temp_dir = 'temp_whatsapp_images'
        self.expiry_hours = 24  # Images expire after 24 hours
    
    def save_base64_image(self, base64_data, original_filename=None):
        """
        Save base64 image data to temporary storage
        Returns: dict with success, file_id, and access_url
        """
        try:
            # Extract base64 data and format
            if base64_data.startswith('data:'):
                # Remove data:image/jpeg;base64, prefix
                header, data = base64_data.split(',', 1)
                # Extract file extension from header
                format_match = re.search(r'data:image/(\w+)', header)
                file_ext = format_match.group(1) if format_match else 'jpg'
            else:
                data = base64_data
                file_ext = 'jpg'
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}.{file_ext}"
            file_path = f"{self.temp_dir}/{filename}"
            
            # Decode base64 and save
            image_data = base64.b64decode(data)
            file_content = ContentFile(image_data, name=filename)
            
            # Save file
            saved_path = default_storage.save(file_path, file_content)
            
            # Create metadata
            metadata = {
                'file_id': file_id,
                'original_filename': original_filename or filename,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=self.expiry_hours)).isoformat(),
                'file_path': saved_path,
                'file_size': len(image_data)
            }
            
            # Save metadata
            metadata_path = f"{self.temp_dir}/{file_id}.json"
            metadata_content = ContentFile(json.dumps(metadata).encode(), name=f"{file_id}.json")
            default_storage.save(metadata_path, metadata_content)
            
            return {
                'success': True,
                'file_id': file_id,
                'access_url': f'/temp-image/{file_id}/',
                'expires_at': metadata['expires_at'],
                'file_size': metadata['file_size']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_uploaded_file(self, uploaded_file):
        """
        Save uploaded file to temporary storage
        """
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_ext = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'jpg'
            filename = f"{file_id}.{file_ext}"
            file_path = f"{self.temp_dir}/{filename}"
            
            # Save file
            saved_path = default_storage.save(file_path, uploaded_file)
            
            # Create metadata
            metadata = {
                'file_id': file_id,
                'original_filename': uploaded_file.name,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=self.expiry_hours)).isoformat(),
                'file_path': saved_path,
                'file_size': uploaded_file.size
            }
            
            # Save metadata
            metadata_path = f"{self.temp_dir}/{file_id}.json"
            metadata_content = ContentFile(json.dumps(metadata).encode(), name=f"{file_id}.json")
            default_storage.save(metadata_path, metadata_content)
            
            return {
                'success': True,
                'file_id': file_id,
                'access_url': f'/temp-image/{file_id}/',
                'expires_at': metadata['expires_at'],
                'file_size': metadata['file_size']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_info(self, file_id):
        """
        Get file information by file_id
        """
        try:
            metadata_path = f"{self.temp_dir}/{file_id}.json"
            if default_storage.exists(metadata_path):
                with default_storage.open(metadata_path, 'r') as f:
                    content = f.read()
                    if hasattr(content, 'decode'):
                        content = content.decode()
                    metadata = json.loads(content)
                return metadata
            return None
        except Exception as e:
            return None
    
    def serve_file(self, file_id):
        """
        Serve file content for private access
        Returns HttpResponse with image data
        """
        try:
            metadata = self.get_file_info(file_id)
            if not metadata:
                raise Http404("Image not found")
            
            # Check if file has expired
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if datetime.now() > expires_at:
                # Clean up expired file
                self.cleanup_file(file_id)
                raise Http404("Image expired")
            
            # Serve file
            file_path = metadata['file_path']
            if default_storage.exists(file_path):
                with default_storage.open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Determine content type
                file_ext = file_path.split('.')[-1].lower()
                content_type_map = {
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'webp': 'image/webp'
                }
                content_type = content_type_map.get(file_ext, 'image/jpeg')
                
                response = HttpResponse(file_data, content_type=content_type)
                response['Content-Length'] = len(file_data)
                response['Cache-Control'] = 'private, max-age=3600'
                return response
            
            raise Http404("Image file not found")
            
        except Exception as e:
            if isinstance(e, Http404):
                raise
            raise Http404("Error serving image")
    
    def cleanup_file(self, file_id):
        """
        Remove file and its metadata
        """
        try:
            metadata = self.get_file_info(file_id)
            if metadata:
                # Delete image file
                if default_storage.exists(metadata['file_path']):
                    default_storage.delete(metadata['file_path'])
                
                # Delete metadata file
                metadata_path = f"{self.temp_dir}/{file_id}.json"
                if default_storage.exists(metadata_path):
                    default_storage.delete(metadata_path)
            
            return True
        except Exception as e:
            return False
    
    def cleanup_expired_files(self):
        """
        Clean up all expired files
        Should be called periodically (e.g., via Django management command)
        """
        try:
            # List all metadata files
            temp_files = default_storage.listdir(self.temp_dir)[1]  # Get files, not directories
            json_files = [f for f in temp_files if f.endswith('.json')]
            
            cleaned_count = 0
            for json_file in json_files:
                file_id = json_file.replace('.json', '')
                metadata = self.get_file_info(file_id)
                
                if metadata:
                    expires_at = datetime.fromisoformat(metadata['expires_at'])
                    if datetime.now() > expires_at:
                        self.cleanup_file(file_id)
                        cleaned_count += 1
            
            return {'success': True, 'cleaned_count': cleaned_count}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

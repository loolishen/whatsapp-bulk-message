"""
Cloudinary Image Service for WhatsApp Bulk Message
Handles image uploads to Cloudinary for reliable cloud hosting
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import tempfile
import os
import base64
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class CloudinaryImageService:
    """Service for handling image uploads to Cloudinary"""
    
    def __init__(self):
        """Initialize Cloudinary configuration"""
        cloudinary.config( 
            cloud_name="dzbje38xw", 
            api_key="645993869662484", 
            api_secret="43OPTPwCt8cWEim-L9GHtwmj7_w",
            secure=True
        )
    
    def upload_file(self, uploaded_file):
        """
        Upload a Django uploaded file to Cloudinary
        
        Args:
            uploaded_file: Django UploadedFile object
            
        Returns:
            dict: {'success': bool, 'url': str, 'public_id': str, 'error': str}
        """
        try:
            # Generate a unique public_id
            public_id = f"whatsapp_bulk/{uploaded_file.name}_{self._generate_timestamp()}"
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                uploaded_file,
                public_id=public_id,
                folder="whatsapp_bulk",
                resource_type="image",
                quality="auto:good",
                format="jpg"  # Standardize format for WhatsApp compatibility
            )
            
            logger.info(f"✅ Successfully uploaded image to Cloudinary: {upload_result['secure_url']}")
            
            return {
                'success': True,
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id'],
                'width': upload_result.get('width'),
                'height': upload_result.get('height'),
                'format': upload_result.get('format'),
                'bytes': upload_result.get('bytes')
            }
            
        except Exception as e:
            logger.error(f"❌ Cloudinary upload failed: {str(e)}")
            return {
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }
    
    def upload_base64(self, base64_data, filename="image.jpg"):
        """
        Upload a base64 encoded image to Cloudinary
        
        Args:
            base64_data: Base64 encoded image data (with or without data URL prefix)
            filename: Original filename for reference
            
        Returns:
            dict: {'success': bool, 'url': str, 'public_id': str, 'error': str}
        """
        try:
            # Clean base64 data
            if base64_data.startswith('data:image'):
                # Remove data URL prefix
                base64_data = base64_data.split(',')[1]
            
            # Generate a unique public_id
            public_id = f"whatsapp_bulk/{filename}_{self._generate_timestamp()}"
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                f"data:image/jpeg;base64,{base64_data}",
                public_id=public_id,
                folder="whatsapp_bulk",
                resource_type="image",
                quality="auto:good",
                format="jpg"
            )
            
            logger.info(f"✅ Successfully uploaded base64 image to Cloudinary: {upload_result['secure_url']}")
            
            return {
                'success': True,
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id'],
                'width': upload_result.get('width'),
                'height': upload_result.get('height'),
                'format': upload_result.get('format'),
                'bytes': upload_result.get('bytes')
            }
            
        except Exception as e:
            logger.error(f"❌ Cloudinary base64 upload failed: {str(e)}")
            return {
                'success': False,
                'error': f'Base64 upload failed: {str(e)}'
            }
    
    def upload_url(self, image_url):
        """
        Upload an image from URL to Cloudinary
        
        Args:
            image_url: URL of the image to upload
            
        Returns:
            dict: {'success': bool, 'url': str, 'public_id': str, 'error': str}
        """
        try:
            # Generate a unique public_id
            public_id = f"whatsapp_bulk/url_upload_{self._generate_timestamp()}"
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                image_url,
                public_id=public_id,
                folder="whatsapp_bulk",
                resource_type="image",
                quality="auto:good",
                format="jpg"
            )
            
            logger.info(f"✅ Successfully uploaded URL image to Cloudinary: {upload_result['secure_url']}")
            
            return {
                'success': True,
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id'],
                'width': upload_result.get('width'),
                'height': upload_result.get('height'),
                'format': upload_result.get('format'),
                'bytes': upload_result.get('bytes')
            }
            
        except Exception as e:
            logger.error(f"❌ Cloudinary URL upload failed: {str(e)}")
            return {
                'success': False,
                'error': f'URL upload failed: {str(e)}'
            }
    
    def delete_image(self, public_id):
        """
        Delete an image from Cloudinary
        
        Args:
            public_id: The public ID of the image to delete
            
        Returns:
            dict: {'success': bool, 'result': str}
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            logger.info(f"🗑️ Deleted image from Cloudinary: {public_id}")
            
            return {
                'success': True,
                'result': result.get('result', 'deleted')
            }
            
        except Exception as e:
            logger.error(f"❌ Cloudinary delete failed: {str(e)}")
            return {
                'success': False,
                'error': f'Delete failed: {str(e)}'
            }
    
    def get_optimized_url(self, public_id, width=None, height=None, quality="auto:good"):
        """
        Get an optimized URL for an uploaded image
        
        Args:
            public_id: The public ID of the uploaded image
            width: Optional width for resizing
            height: Optional height for resizing
            quality: Image quality setting
            
        Returns:
            str: Optimized image URL
        """
        try:
            options = {
                'quality': quality,
                'fetch_format': 'auto'
            }
            
            if width:
                options['width'] = width
            if height:
                options['height'] = height
            if width or height:
                options['crop'] = 'fill'
            
            url, _ = cloudinary_url(public_id, **options)
            return url
            
        except Exception as e:
            logger.error(f"❌ Failed to generate optimized URL: {str(e)}")
            return None
    
    def _generate_timestamp(self):
        """Generate timestamp for unique public_id"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    def test_connection(self):
        """
        Test Cloudinary connection and configuration
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Try to get account details
            result = cloudinary.api.usage()
            
            return {
                'success': True,
                'message': f'✅ Cloudinary connected successfully. Credits used: {result.get("credits", {}).get("usage", 0)}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Cloudinary connection failed: {str(e)}'
            }

# Global instance
cloudinary_service = CloudinaryImageService()

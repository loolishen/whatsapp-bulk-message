"""
Test Cloudinary Integration for WhatsApp Bulk Message
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.cloudinary_service import cloudinary_service
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

def test_cloudinary_connection():
    """Test if Cloudinary is properly configured"""
    print("🔍 Testing Cloudinary Connection...")
    result = cloudinary_service.test_connection()
    print(f"Connection Status: {result['message']}")
    return result['success']

def test_file_upload():
    """Test uploading a sample image file"""
    print("\n📤 Testing File Upload...")
    
    # Create a simple test image (1x1 pixel GIF)
    test_content = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
    test_file = SimpleUploadedFile('test_image.gif', test_content, content_type='image/gif')
    
    # Upload using our service
    result = cloudinary_service.upload_file(test_file)
    
    if result['success']:
        print(f"✅ Upload successful!")
        print(f"   📍 URL: {result['url']}")
        print(f"   🆔 Public ID: {result['public_id']}")
        print(f"   📏 Dimensions: {result.get('width')}x{result.get('height')}")
        print(f"   💾 Size: {result.get('bytes')} bytes")
        return result
    else:
        print(f"❌ Upload failed: {result['error']}")
        return None

def test_django_endpoint():
    """Test the Django upload endpoint"""
    print("\n🌐 Testing Django Upload Endpoint...")
    
    client = Client()
    
    # Create test image
    test_content = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
    test_file = SimpleUploadedFile('test_upload.gif', test_content, content_type='image/gif')
    
    # Upload via Django endpoint
    response = client.post('/upload-image/', {'image': test_file})
    
    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        
        if data.get('success'):
            print(f"✅ Django endpoint upload successful!")
            print(f"   📍 URL: {data['file_url']}")
            print(f"   🆔 Public ID: {data.get('public_id')}")
            print(f"   💾 Storage: {data.get('storage_type')}")
            print(f"   📏 Dimensions: {data.get('width')}x{data.get('height')}")
            return data
        else:
            print(f"❌ Django endpoint failed: {data.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.content}")
    
    return None

def test_base64_upload():
    """Test base64 image upload"""
    print("\n🔧 Testing Base64 Upload...")
    
    # Simple base64 encoded 1x1 pixel red dot PNG
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    result = cloudinary_service.upload_base64(base64_data, "test_base64.png")
    
    if result['success']:
        print(f"✅ Base64 upload successful!")
        print(f"   📍 URL: {result['url']}")
        print(f"   🆔 Public ID: {result['public_id']}")
        return result
    else:
        print(f"❌ Base64 upload failed: {result['error']}")
        return None

if __name__ == "__main__":
    print("🚀 Cloudinary Integration Test Suite")
    print("=" * 50)
    
    # Test 1: Connection
    if not test_cloudinary_connection():
        print("❌ Cloudinary connection failed. Check your credentials!")
        sys.exit(1)
    
    # Test 2: File Upload
    file_result = test_file_upload()
    
    # Test 3: Django Endpoint
    django_result = test_django_endpoint()
    
    # Test 4: Base64 Upload
    base64_result = test_base64_upload()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"✅ Cloudinary Connection: {'PASS' if True else 'FAIL'}")
    print(f"✅ File Upload: {'PASS' if file_result else 'FAIL'}")
    print(f"✅ Django Endpoint: {'PASS' if django_result else 'FAIL'}")
    print(f"✅ Base64 Upload: {'PASS' if base64_result else 'FAIL'}")
    
    if file_result and django_result and base64_result:
        print("\n🎉 ALL TESTS PASSED! Cloudinary integration is working perfectly!")
        
        # Show the URLs for manual verification
        print("\n🔗 Test URLs (you can open these to verify):")
        if file_result:
            print(f"   File Upload: {file_result['url']}")
        if django_result:
            print(f"   Django Upload: {django_result['file_url']}")
        if base64_result:
            print(f"   Base64 Upload: {base64_result['url']}")
            
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")

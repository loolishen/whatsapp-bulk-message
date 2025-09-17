"""
Debug webhook to see what WABOT is sending
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST", "GET"])
def debug_webhook(request):
    """Debug webhook to see what WABOT sends"""
    print("=" * 50)
    print("DEBUG WEBHOOK REQUEST")
    print("=" * 50)
    print(f"Method: {request.method}")
    print(f"Content-Type: {request.META.get('CONTENT_TYPE', 'Not set')}")
    print(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Not set')}")
    print(f"Body: {request.body}")
    print("=" * 50)
    
    try:
        data = json.loads(request.body)
        print(f"Parsed JSON: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Could not parse as JSON: {e}")
    
    return JsonResponse({'status': 'received', 'message': 'Debug webhook received'})


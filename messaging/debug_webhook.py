"""
Debug Webhook Handler for testing webhook functionality
"""
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def debug_webhook(request):
    """
    Debug webhook endpoint for testing webhook functionality
    """
    try:
        if request.method == 'GET':
            # Handle webhook verification
            verify_token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')
            
            if verify_token == 'debug_token':
                return HttpResponse(challenge)
            else:
                return HttpResponse('Verification failed', status=403)
        
        elif request.method == 'POST':
            # Log incoming webhook data
            try:
                data = json.loads(request.body)
                logger.info(f"Debug webhook received data: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in debug webhook request: {request.body}")
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            # Return success response
            return JsonResponse({
                'status': 'success',
                'message': 'Debug webhook processed successfully',
                'received_data': data
            })
    
    except Exception as e:
        logger.error(f"Debug webhook error: {str(e)}")
        return JsonResponse({'error': 'Debug webhook processing failed'}, status=500)

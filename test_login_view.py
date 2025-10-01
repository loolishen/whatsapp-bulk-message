
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_login(request):
    """Simple test login endpoint"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        if username == 'tenant' and password == 'Tenant123!':
            return JsonResponse({'status': 'success', 'message': 'Login successful'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
    
    return JsonResponse({'status': 'info', 'message': 'Send POST with username and password'})

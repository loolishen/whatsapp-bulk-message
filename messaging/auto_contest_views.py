"""
Views for managing and monitoring automatic contest functionality
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import Tenant, Contest, ContestEntry, Customer
from .step_by_step_contest_service import StepByStepContestService
from .views import _get_tenant, _require_plan

@login_required
def auto_contest_dashboard(request):
    """Dashboard for monitoring automatic contest functionality"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    step_contest_service = StepByStepContestService()
    stats = step_contest_service.get_flow_stats(tenant)
    
    # Get recent contest entries
    recent_entries = ContestEntry.objects.filter(
        tenant=tenant
    ).select_related('contest', 'customer').order_by('-submitted_at')[:20]
    
    # Get active contests with entry counts
    active_contests = Contest.objects.filter(
        tenant=tenant,
        is_active=True,
        starts_at__lte=timezone.now(),
        ends_at__gte=timezone.now()
    ).order_by('-created_at')
    
    context = {
        'tenant': tenant,
        'stats': stats,
        'recent_entries': recent_entries,
        'active_contests': active_contests,
    }
    
    return render(request, 'messaging/auto_contest_dashboard.html', context)

@login_required
def auto_contest_settings(request):
    """Settings for automatic contest functionality"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Handle settings updates
        auto_enable = request.POST.get('auto_enable') == 'on'
        # Add more settings as needed
        
        messages.success(request, 'Auto contest settings updated successfully!')
        return redirect('auto_contest_settings')
    
    context = {
        'tenant': tenant,
    }
    
    return render(request, 'messaging/auto_contest_settings.html', context)

@login_required
def auto_contest_test(request):
    """Test automatic contest functionality"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        message_text = request.POST.get('message_text', '').strip()
        
        if not phone_number or not message_text:
            messages.error(request, 'Please provide both phone number and message text')
            return redirect('auto_contest_test')
        
        try:
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'name': f'Test Customer {phone_number[-4:]}',
                    'tenant': tenant,
                    'gender': 'N/A',
                    'marital_status': 'N/A'
                }
            )
            
            # Test step-by-step contest service
            step_contest_service = StepByStepContestService()
            results = step_contest_service.process_message_for_contests(
                customer, message_text, tenant
            )
            
            if results['flows_processed'] > 0:
                messages.success(request, f'Test successful! {results["flows_processed"]} flows processed, {results["flows_created"]} flows created, {results["flows_advanced"]} flows advanced')
            else:
                messages.warning(request, 'Test completed but no contest flows were processed')
            
            if results['errors']:
                for error in results['errors']:
                    messages.error(request, f'Error: {error}')
            
        except Exception as e:
            messages.error(request, f'Test failed: {str(e)}')
        
        return redirect('auto_contest_test')
    
    context = {
        'tenant': tenant,
    }
    
    return render(request, 'messaging/auto_contest_test.html', context)

@login_required
def auto_contest_stats_api(request):
    """API endpoint for contest statistics"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        step_contest_service = StepByStepContestService()
        stats = step_contest_service.get_flow_stats(tenant)
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

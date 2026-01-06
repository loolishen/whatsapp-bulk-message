"""
URL configuration for whatsapp_bulk project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from messaging.whatsapp_webhook import whatsapp_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('messaging.urls')),
    path("webhook/whatsapp/", whatsapp_webhook),
    path("webhook/whatsapp", whatsapp_webhook),
    path("health", lambda request: JsonResponse({"status": "ok"})),
    path("health/", lambda request: JsonResponse({"status": "ok"})),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.conf import settings


def relief_app_context(request):
    """Add relief app configuration and contact info to template context"""
    return {
        'contact_phone': settings.CONTACT_INFO['phone'],
        'contact_email': settings.CONTACT_INFO['email'], 
        'organization_name': settings.CONTACT_INFO['organization_name'],
        'relief_config': settings.RELIEF_APP_CONFIG,
    }
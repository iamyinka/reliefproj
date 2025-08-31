"""
URL configuration for reliefproj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

# Mock views for static pages
class HomeView(TemplateView):
    template_name = 'pages/home.html'

class PackagesView(TemplateView):
    template_name = 'pages/packages.html'

class ApplyView(TemplateView):
    template_name = 'pages/apply.html'

class StatusView(TemplateView):
    template_name = 'pages/status.html'

class PickupView(TemplateView):
    template_name = 'pages/pickup.html'

# Supervisor views
class SupervisorDashboardView(TemplateView):
    template_name = 'supervisor/dashboard.html'

class SupervisorApplicationsView(TemplateView):
    template_name = 'supervisor/applications.html'

class SupervisorPackagesView(TemplateView):
    template_name = 'supervisor/packages.html'

class SupervisorScheduleView(TemplateView):
    template_name = 'supervisor/schedule.html'

class SupervisorScannerView(TemplateView):
    template_name = 'supervisor/scanner.html'

class SupervisorReportsView(TemplateView):
    template_name = 'supervisor/reports.html'

class SupervisorNotificationsView(TemplateView):
    template_name = 'supervisor/notifications.html'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/applications/', include('applications.urls')),
    path('api/packages/', include('packages.urls')),
    path('api/pickups/', include('pickups.urls')),
    path('api/auth/', include('rest_framework.urls')),
    
    # Frontend routes
    path('', HomeView.as_view(), name='home'),
    path('packages/', PackagesView.as_view(), name='packages'),
    path('apply/', ApplyView.as_view(), name='apply'),
    path('status/', StatusView.as_view(), name='status'),
    path('pickup/', PickupView.as_view(), name='pickup'),
    
    # Supervisor routes
    path('supervisor/', SupervisorDashboardView.as_view(), name='supervisor_dashboard'),
    path('supervisor/applications/', SupervisorApplicationsView.as_view(), name='supervisor_applications'),
    path('supervisor/packages/', SupervisorPackagesView.as_view(), name='supervisor_packages'),
    path('supervisor/schedule/', SupervisorScheduleView.as_view(), name='supervisor_schedule'),
    path('supervisor/scanner/', SupervisorScannerView.as_view(), name='supervisor_scanner'),
    path('supervisor/reports/', SupervisorReportsView.as_view(), name='supervisor_reports'),
    path('supervisor/notifications/', SupervisorNotificationsView.as_view(), name='supervisor_notifications'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

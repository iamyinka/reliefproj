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
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from core import views

# Staff-only access mixin
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require staff authentication for supervisor pages"""
    login_url = reverse_lazy('staff_login')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        # User is authenticated but not staff
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(self.request, 'Access denied. Staff privileges required.')
        return redirect('home')

# Supervisor views with staff authentication
class SupervisorDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'supervisor/dashboard.html'

class SupervisorApplicationsView(StaffRequiredMixin, TemplateView):
    template_name = 'supervisor/applications.html'

class SupervisorPackagesView(StaffRequiredMixin, TemplateView):
    template_name = 'supervisor/packages.html'

class SupervisorScheduleView(StaffRequiredMixin, TemplateView):
    template_name = 'supervisor/schedule.html'

class SupervisorScannerView(StaffRequiredMixin, TemplateView):
    template_name = 'supervisor/scanner.html'

class SupervisorReportsView(StaffRequiredMixin, TemplateView):
    template_name = 'supervisor/reports.html'

class SupervisorNotificationsView(StaffRequiredMixin, TemplateView):
    template_name = 'supervisor/notifications.html'

# Custom staff login view
class StaffLoginView(LoginView):
    template_name = 'auth/staff_login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirect staff users to supervisor dashboard
        if self.request.user.is_staff:
            return reverse_lazy('supervisor_dashboard')
        # Regular users go to home
        return reverse_lazy('home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Check if user is staff after login
        if not self.request.user.is_staff:
            from django.contrib import messages
            messages.warning(self.request, 'You need staff privileges to access the supervisor area.')
        return response

# Simple function-based logout view
def logout_view(request):
    from django.contrib.auth import logout
    from django.contrib import messages
    from django.shortcuts import redirect
    
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
    
    return redirect('home')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/applications/', include('applications.urls')),
    path('api/packages/', include('packages.urls')),
    path('api/pickups/', include('pickups.urls')),
    path('api/auth/', include('rest_framework.urls')),
    
    # Authentication routes
    path('staff-login/', StaffLoginView.as_view(), name='staff_login'),
    path('logout/', logout_view, name='logout'),
    
    # Frontend routes
    path('', views.home, name='home'),
    path('packages/', views.packages, name='packages'),
    path('apply/', views.apply, name='apply'),
    path('status/', views.status, name='status'),
    path('pickup/', views.pickup, name='pickup'),
    
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

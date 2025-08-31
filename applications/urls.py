from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_application, name='submit_application'),
    path('list/', views.ApplicationListView.as_view(), name='application_list'),
    path('<uuid:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('<uuid:application_id>/approve/', views.approve_application, name='approve_application'),
    path('<uuid:application_id>/reject/', views.reject_application, name='reject_application'),
]
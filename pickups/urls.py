from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.PickupListView.as_view(), name='pickup_list'),
    path('<int:pk>/', views.PickupDetailView.as_view(), name='pickup_detail'),
    path('verify-qr/', views.verify_qr_code, name='verify_qr_code'),
    path('<int:pickup_id>/complete/', views.complete_pickup, name='complete_pickup'),
    path('status/<str:pickup_code>/', views.pickup_status, name='pickup_status'),
]
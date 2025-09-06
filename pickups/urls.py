from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.PickupListView.as_view(), name='pickup_list'),
    path('<int:pk>/', views.PickupDetailView.as_view(), name='pickup_detail'),
    path('verify/', views.verify_qr_code, name='verify_qr_code'),
    path('confirm/', views.confirm_pickup, name='confirm_pickup'),
    path('today-queue/', views.today_pickup_queue, name='today_pickup_queue'),
    path('recent/', views.recent_scans, name='recent_scans'),
    path('<int:pickup_id>/complete/', views.complete_pickup, name='complete_pickup'),
    path('status/<str:pickup_code>/', views.pickup_status, name='pickup_status'),
]
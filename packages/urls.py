from django.urls import path
from . import views

urlpatterns = [
    path('available/', views.PackageListView.as_view(), name='available_packages'),
    path('manage/', views.PackageManagementView.as_view(), name='package_management'),
    path('manage/<int:pk>/', views.PackageDetailView.as_view(), name='package_detail'),
    path('<int:package_id>/restock/', views.restock_package, name='restock_package'),
]
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Package
from .serializers import PackageSerializer, PackageListSerializer


class PackageListView(generics.ListAPIView):
    """List available packages for application form"""
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageListSerializer
    permission_classes = [permissions.AllowAny]


class PackageManagementView(generics.ListCreateAPIView):
    """List and create packages - for supervisors"""
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only allow staff users to access this endpoint
        if not self.request.user.is_staff:
            return Package.objects.none()
        return super().get_queryset()


class PackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, delete single package - for supervisors"""
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only allow staff users to access this endpoint
        if not self.request.user.is_staff:
            return Package.objects.none()
        return super().get_queryset()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def restock_package(request, package_id):
    """Add stock to a package"""
    # Only allow staff users to restock packages
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': 'Staff privileges required.'
        }, status=403)
        
    try:
        package = Package.objects.get(id=package_id)
        quantity = int(request.data.get('quantity', 0))
        
        if quantity <= 0:
            return Response({
                'success': False,
                'message': 'Quantity must be greater than 0.'
            }, status=400)
        
        package.restock(quantity)
        
        return Response({
            'success': True,
            'message': f'Added {quantity} units. Total available: {package.available_quantity}',
            'available_quantity': package.available_quantity
        })
        
    except Package.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Package not found.'
        }, status=404)
    except ValueError:
        return Response({
            'success': False,
            'message': 'Invalid quantity provided.'
        }, status=400)

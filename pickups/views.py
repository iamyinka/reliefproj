from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Pickup
from .serializers import PickupSerializer, QRCodeVerificationSerializer


class PickupListView(generics.ListAPIView):
    """List all pickups - for supervisors"""
    queryset = Pickup.objects.all()
    serializer_class = PickupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        date_filter = self.request.query_params.get('date', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_filter:
            queryset = queryset.filter(scheduled_date=date_filter)
            
        return queryset.order_by('scheduled_date', 'scheduled_time')


class PickupDetailView(generics.RetrieveAPIView):
    """Get single pickup details - for supervisors"""
    queryset = Pickup.objects.all()
    serializer_class = PickupSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_qr_code(request):
    """Verify QR code for pickup"""
    serializer = QRCodeVerificationSerializer(data=request.data)
    if serializer.is_valid():
        pickup_code = serializer.validated_data['pickup_code']
        
        try:
            pickup = Pickup.objects.get(pickup_code=pickup_code)
            
            # Return pickup details for verification
            return Response({
                'success': True,
                'pickup': {
                    'id': pickup.id,
                    'pickup_code': pickup.pickup_code,
                    'applicant_name': pickup.application.get_full_name(),
                    'phone': pickup.application.phone,
                    'selected_package': pickup.application.selected_package,
                    'scheduled_date': pickup.scheduled_date,
                    'scheduled_time': pickup.scheduled_time,
                    'status': pickup.status
                }
            })
            
        except Pickup.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid QR code.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_pickup(request, pickup_id):
    """Mark pickup as completed"""
    try:
        pickup = Pickup.objects.get(id=pickup_id)
        
        if pickup.status == 'COMPLETED':
            return Response({
                'success': False,
                'message': 'This pickup has already been completed.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if pickup.is_expired:
            return Response({
                'success': False,
                'message': 'This QR code has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark as completed
        pickup.complete_pickup(request.user)
        pickup.notes = request.data.get('notes', '')
        pickup.save()
        
        return Response({
            'success': True,
            'message': 'Pickup completed successfully!',
            'pickup': {
                'pickup_code': pickup.pickup_code,
                'applicant_name': pickup.application.get_full_name(),
                'completed_at': pickup.picked_up_at,
                'completed_by': request.user.get_full_name()
            }
        })
        
    except Pickup.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Pickup not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def pickup_status(request, pickup_code):
    """Check pickup status by code - for applicants"""
    try:
        pickup = Pickup.objects.get(pickup_code=pickup_code)
        
        return Response({
            'success': True,
            'pickup': {
                'pickup_code': pickup.pickup_code,
                'status': pickup.status,
                'scheduled_date': pickup.scheduled_date,
                'scheduled_time': pickup.scheduled_time,
                'is_expired': pickup.is_expired,
                'applicant_name': pickup.application.get_full_name(),
                'selected_package': pickup.application.selected_package
            }
        })
        
    except Pickup.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Pickup not found.'
        }, status=status.HTTP_404_NOT_FOUND)

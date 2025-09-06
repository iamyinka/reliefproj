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
        # Only allow staff users to access this endpoint
        if not self.request.user.is_staff:
            return Pickup.objects.none()
            
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
    
    def get_queryset(self):
        # Only allow staff users to access this endpoint
        if not self.request.user.is_staff:
            return Pickup.objects.none()
        return super().get_queryset()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_qr_code(request):
    """Verify QR code for pickup - used by scanner"""
    pickup_code = request.data.get('pickup_code', '').strip()
    
    if not pickup_code:
        return Response({
            'success': False,
            'message': 'Pickup code is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        pickup = Pickup.objects.select_related('application').get(pickup_code=pickup_code)
        
        # Check if pickup is valid
        if pickup.status == 'COMPLETED':
            return Response({
                'success': False,
                'message': 'This package has already been collected.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if pickup.status == 'CANCELLED':
            return Response({
                'success': False,
                'message': 'This pickup has been cancelled.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if pickup.is_expired:
            return Response({
                'success': False,
                'message': f'This QR code has expired. Valid until {pickup.scheduled_date + timezone.timedelta(days=1)}.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get package details
        def get_package_name(package_type):
            package_names = {
                'small_basic': 'Small Family Basic',
                'medium_basic': 'Medium Family Basic', 
                'large_basic': 'Large Family Basic',
                'emergency': 'Emergency Relief',
                'senior': 'Senior Citizen Special'
            }
            return package_names.get(package_type, package_type)
        
        def get_package_contents(package_type):
            # Get real package contents from packages app
            try:
                from packages.models import Package
                package = Package.objects.filter(package_type=package_type, is_active=True).first()
                if package:
                    contents = []
                    
                    # Add items from items_included JSON field if available
                    if hasattr(package, 'items_included') and package.items_included:
                        if isinstance(package.items_included, list):
                            contents.extend(package.items_included)
                        elif isinstance(package.items_included, dict):
                            # Handle dictionary format like {'rice': '3 Congo of Rice'}
                            for key, value in package.items_included.items():
                                contents.append(value)
                    
                    # Add items from related PackageItem model if available  
                    if hasattr(package, 'package_items'):
                        package_items = package.package_items.all()
                        for item in package_items:
                            contents.append(f"{item.quantity} {item.item_name}")
                    
                    # Add cash amount if specified
                    if package.cash_amount and package.cash_amount > 0:
                        contents.append(f"₦{package.cash_amount:,} Cash")
                    
                    if contents:
                        return ', '.join(contents)
                    elif package.description:
                        return package.description
                        
            except ImportError:
                pass
            except Exception as e:
                print(f"Error fetching package contents: {e}")
            
            # Fallback to hardcoded values if package not found
            package_contents = {
                'small_basic': '5kg Rice, 2kg Beans, 1L Vegetable Oil, 1kg Salt, ₦5,000 Cash',
                'medium_basic': '10kg Rice, 5kg Beans, 2L Vegetable Oil, 1kg Salt, 1kg Sugar, ₦8,000 Cash',
                'large_basic': '25kg Rice, 10kg Beans, 3L Vegetable Oil, 2kg Salt, 2kg Sugar, ₦15,000 Cash',
                'emergency': 'Emergency Relief Package + ₦10,000 Cash',
                'senior': 'Senior Citizen Special Package + ₦6,000 Cash'
            }
            return package_contents.get(package_type, 'Package contents not specified')
        
        def get_time_display(time_slot):
            time_slots = {
                'morning': '9:00 AM - 12:00 PM',
                'afternoon': '1:00 PM - 4:00 PM', 
                'evening': '4:00 PM - 6:00 PM'
            }
            return time_slots.get(time_slot, time_slot)
        
        # Return pickup details for verification
        return Response({
            'success': True,
            'data': {
                'pickup_id': pickup.id,
                'pickup_code': pickup.pickup_code,
                'applicant_name': pickup.application.get_full_name(),
                'phone': pickup.application.phone,
                'reference_number': pickup.application.reference_number,
                'package_name': get_package_name(pickup.application.selected_package),
                'package_contents': get_package_contents(pickup.application.selected_package),
                'scheduled_date': pickup.scheduled_date.strftime('%Y-%m-%d'),
                'scheduled_time': get_time_display(pickup.scheduled_time),
                'expiry_date': (pickup.scheduled_date + timezone.timedelta(days=7)).strftime('%Y-%m-%d'),
                'status': pickup.status,
                'is_expired': pickup.is_expired
            }
        })
        
    except Pickup.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invalid pickup code. Please check the code and try again.'
        }, status=status.HTTP_404_NOT_FOUND)


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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_pickup(request):
    """Confirm/complete a pickup - used by scanner"""
    pickup_id = request.data.get('pickup_id')
    notes = request.data.get('notes', 'Package collected via QR scanner')
    
    if not pickup_id:
        return Response({
            'success': False,
            'message': 'Pickup ID is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        pickup = Pickup.objects.select_related('application').get(id=pickup_id)
        
        if pickup.status == 'COMPLETED':
            return Response({
                'success': False,
                'message': 'This package has already been collected.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if pickup.is_expired:
            return Response({
                'success': False,
                'message': 'This QR code has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Complete the pickup
        pickup.complete_pickup(request.user)
        pickup.notes = notes
        pickup.save()
        
        return Response({
            'success': True,
            'message': f'Pickup confirmed for {pickup.application.get_full_name()}!',
            'data': {
                'pickup_code': pickup.pickup_code,
                'applicant_name': pickup.application.get_full_name(),
                'completed_at': pickup.picked_up_at.isoformat() if pickup.picked_up_at else None,
                'completed_by': request.user.get_full_name() or request.user.username
            }
        })
        
    except Pickup.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Pickup record not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def today_pickup_queue(request):
    """Get today's pickup queue for sidebar display"""
    today = timezone.now().date()
    
    pickups = Pickup.objects.select_related('application').filter(
        scheduled_date=today,
        status__in=['SCHEDULED', 'CONFIRMED']
    ).order_by('scheduled_time')
    
    pickup_data = []
    for pickup in pickups:
        pickup_data.append({
            'id': pickup.id,
            'applicant_name': pickup.application.get_full_name(),
            'reference_number': pickup.application.reference_number,
            'pickup_code': pickup.pickup_code,
            'scheduled_time': pickup.scheduled_time,
            'status': pickup.status,
            'package_type': pickup.application.selected_package
        })
    
    return Response({
        'success': True,
        'pickups': pickup_data,
        'total_count': len(pickup_data)
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_scans(request):
    """Get recent pickup scans for scanner page"""
    limit = int(request.GET.get('limit', 10))
    
    recent_pickups = Pickup.objects.select_related('application').filter(
        status='COMPLETED'
    ).order_by('-picked_up_at')[:limit]
    
    scan_data = []
    for pickup in recent_pickups:
        scan_data.append({
            'id': pickup.id,
            'pickup_code': pickup.pickup_code,
            'applicant_name': pickup.application.get_full_name(),
            'reference_number': pickup.application.reference_number,
            'package_type': pickup.application.selected_package,
            'completed_at': pickup.picked_up_at.isoformat() if pickup.picked_up_at else None,
            'completed_by': pickup.picked_up_by.get_full_name() if pickup.picked_up_by else 'System',
            'notes': pickup.notes or 'Package collected successfully'
        })
    
    return Response({
        'success': True,
        'scans': scan_data,
        'total_count': len(scan_data)
    })


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
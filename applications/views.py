from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Application
from .serializers import ApplicationSerializer, ApplicationSubmissionSerializer, ApplicationReviewSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def submit_application(request):
    """Anonymous application submission endpoint"""
    serializer = ApplicationSubmissionSerializer(data=request.data)
    if serializer.is_valid():
        application = serializer.save()
        
        # Return success response with reference number
        return Response({
            'success': True,
            'message': 'Application submitted successfully!',
            'reference_number': application.reference_number,
            'data': {
                'id': application.id,
                'reference_number': application.reference_number,
                'full_name': application.get_full_name(),
                'phone': application.phone,
                'selected_package': application.selected_package,
                'status': application.status
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Please correct the errors below.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


class ApplicationListView(generics.ListAPIView):
    """List all applications - for supervisors"""
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-created_at')


class ApplicationDetailView(generics.RetrieveAPIView):
    """Get single application details - for supervisors"""
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_application(request, application_id):
    """Approve an application"""
    try:
        application = Application.objects.get(id=application_id)
        if application.status != 'PENDING':
            return Response({
                'success': False,
                'message': 'Only pending applications can be approved.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'APPROVED'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.review_notes = request.data.get('notes', '')
        application.save()
        
        # Create pickup record
        from pickups.models import Pickup
        pickup = Pickup.objects.create(
            application=application,
            scheduled_date=application.preferred_date,
            scheduled_time=application.preferred_time
        )
        
        return Response({
            'success': True,
            'message': 'Application approved successfully!',
            'pickup_code': pickup.pickup_code
        })
        
    except Application.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Application not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_application(request, application_id):
    """Reject an application"""
    try:
        application = Application.objects.get(id=application_id)
        if application.status != 'PENDING':
            return Response({
                'success': False,
                'message': 'Only pending applications can be rejected.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'REJECTED'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.review_notes = request.data.get('notes', '')
        application.save()
        
        return Response({
            'success': True,
            'message': 'Application rejected.'
        })
        
    except Application.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Application not found.'
        }, status=status.HTTP_404_NOT_FOUND)

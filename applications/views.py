from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Application
from .serializers import ApplicationSerializer, ApplicationSubmissionSerializer, ApplicationReviewSerializer
import re


def is_valid_nigerian_phone(phone):
    """
    Validate Nigerian phone number format
    Accepts formats: 08012345678, +2348012345678, 2348012345678
    """
    if not phone:
        return False
    
    # Remove spaces, dashes, and other non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    # Nigerian phone number patterns
    patterns = [
        r'^0[789][01]\d{8}$',           # 08012345678 (local format)
        r'^\+2348[01]\d{8}$',           # +2348012345678 (international)
        r'^2348[01]\d{8}$',             # 2348012345678 (without +)
    ]
    
    return any(re.match(pattern, cleaned) for pattern in patterns)


def can_user_apply(phone_number):
    """
    Check if a user can submit a new application based on business rules:
    1. No recent application within restriction days (21 days default)
    2. Exception: If last application was REJECTED
    3. Exception: If last approved application expired and wasn't picked up
    """
    restriction_days = settings.RELIEF_APP_CONFIG.get('APPLICATION_RESTRICTION_DAYS', 21)
    cutoff_date = timezone.now().date() - timedelta(days=restriction_days)
    
    # Get the most recent application for this phone number
    recent_application = Application.objects.filter(
        phone=phone_number
    ).order_by('-created_at').first()
    
    if not recent_application:
        # No previous applications, user can apply
        return True, None
    
    # If the most recent application is older than restriction period, allow
    if recent_application.created_at.date() <= cutoff_date:
        return True, None
    
    # Check exceptions:
    
    # Exception 1: If most recent application was REJECTED, allow new application
    if recent_application.status == 'REJECTED':
        return True, None
    
    # Exception 2: If most recent application was APPROVED but pickup expired and not collected
    if recent_application.status == 'APPROVED':
        try:
            pickup = recent_application.pickup
            if pickup.is_expired and pickup.status not in ['COMPLETED']:
                # Pickup expired and wasn't collected, allow new application
                return True, None
        except:
            # No pickup record found, this shouldn't happen but allow application
            return True, None
    
    # If we get here, user has a recent application that blocks new submissions
    days_remaining = restriction_days - (timezone.now().date() - recent_application.created_at.date()).days
    
    return False, {
        'recent_application': recent_application,
        'days_remaining': days_remaining,
        'restriction_days': restriction_days
    }


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def submit_application(request):
    """Anonymous application submission endpoint"""
    serializer = ApplicationSubmissionSerializer(data=request.data)
    if serializer.is_valid():
        # Validate phone number format
        phone_number = serializer.validated_data.get('phone')
        if not is_valid_nigerian_phone(phone_number):
            return Response({
                'success': False,
                'message': 'Please enter a valid Nigerian phone number.',
                'errors': {
                    'phone': ['Invalid Nigerian phone number format. Use formats like: 08012345678, +2348012345678']
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user can apply before saving
        can_apply, restriction_info = can_user_apply(phone_number)
        
        if not can_apply:
            # User cannot apply due to recent application
            recent_app = restriction_info['recent_application']
            days_remaining = restriction_info['days_remaining']
            restriction_days = restriction_info['restriction_days']
            
            # Create detailed error message based on application status
            if recent_app.status == 'PENDING':
                message = f"You have a pending application (Ref: {recent_app.reference_number}) submitted on {recent_app.created_at.strftime('%Y-%m-%d')}. Please wait for review before applying again."
            elif recent_app.status == 'APPROVED':
                message = f"You have an approved application (Ref: {recent_app.reference_number}) from {recent_app.created_at.strftime('%Y-%m-%d')}. Please collect your package first, or wait {days_remaining} more days to apply again."
            elif recent_app.status == 'PICKED_UP':
                message = f"You recently collected a relief package on {recent_app.created_at.strftime('%Y-%m-%d')}. You can apply again after {days_remaining} more days (every {restriction_days} days limit)."
            else:
                message = f"You have a recent application from {recent_app.created_at.strftime('%Y-%m-%d')}. You can apply again in {days_remaining} days."
            
            return Response({
                'success': False,
                'message': message,
                'restriction_info': {
                    'recent_application_ref': recent_app.reference_number,
                    'recent_application_date': recent_app.created_at.strftime('%Y-%m-%d'),
                    'recent_application_status': recent_app.status,
                    'days_remaining': days_remaining,
                    'restriction_days': restriction_days
                },
                'errors': {'phone': [message]}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # User can apply, save the application
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
        # Only allow staff users to access this endpoint
        if not self.request.user.is_staff:
            return Application.objects.none()
            
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
    
    def get_queryset(self):
        # Only allow staff users to access this endpoint
        if not self.request.user.is_staff:
            return Application.objects.none()
        return super().get_queryset()


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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_application_status(request):
    """Check application status by phone number OR reference number - anonymous endpoint"""
    phone_number = request.data.get('phone', '').strip()
    reference_number = request.data.get('reference', '').strip()
    
    if not phone_number and not reference_number:
        return Response({
            'success': False,
            'message': 'Either phone number or reference number is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate phone number format if provided
    if phone_number and not is_valid_nigerian_phone(phone_number):
        return Response({
            'success': False,
            'message': 'Please enter a valid Nigerian phone number (e.g., 08012345678, +2348012345678).',
            'errors': {'phone': ['Invalid Nigerian phone number format.']}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Search by reference number first (more specific), then by phone number
    recent_application = None
    
    if reference_number:
        recent_application = Application.objects.filter(
            reference_number=reference_number
        ).first()
        
        if not recent_application:
            return Response({
                'success': False,
                'message': f'No application found with reference number: {reference_number}',
                'can_apply': True
            }, status=status.HTTP_404_NOT_FOUND)
    
    elif phone_number:
        # Get the most recent application for this phone number
        recent_application = Application.objects.filter(
            phone=phone_number
        ).order_by('-created_at').first()
    
    if not recent_application:
        return Response({
            'success': False,
            'message': 'No application found for this phone number.',
            'can_apply': True
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user can apply for a new application (use phone number from found application)
    can_apply, restriction_info = can_user_apply(recent_application.phone)
    
    response_data = {
        'success': True,
        'application': {
            'reference_number': recent_application.reference_number,
            'full_name': recent_application.get_full_name(),
            'status': recent_application.status,
            'selected_package': recent_application.selected_package,
            'submitted_date': recent_application.created_at.strftime('%Y-%m-%d'),
            'phone': recent_application.phone
        },
        'can_apply': can_apply
    }
    
    # Add pickup information if available
    if recent_application.status == 'APPROVED':
        try:
            pickup = recent_application.pickup
            response_data['pickup'] = {
                'pickup_code': pickup.pickup_code,
                'scheduled_date': pickup.scheduled_date.strftime('%Y-%m-%d'),
                'scheduled_time': pickup.scheduled_time,
                'status': pickup.status,
                'is_expired': pickup.is_expired
            }
        except:
            pass
    
    # Add restriction information if user cannot apply
    if not can_apply and restriction_info:
        response_data['restriction_info'] = {
            'days_remaining': restriction_info['days_remaining'],
            'restriction_days': restriction_info['restriction_days']
        }
    
    return Response(response_data)

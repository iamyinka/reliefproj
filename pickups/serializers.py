from rest_framework import serializers
from .models import Pickup
from applications.serializers import ApplicationSerializer


class PickupSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    
    class Meta:
        model = Pickup
        fields = [
            'id', 'pickup_code', 'qr_code_image', 'scheduled_date', 
            'scheduled_time', 'status', 'picked_up_at', 'notes', 'application'
        ]
        read_only_fields = ['pickup_code', 'qr_code_image', 'picked_up_at']


class QRCodeVerificationSerializer(serializers.Serializer):
    pickup_code = serializers.CharField(max_length=50)
    
    def validate_pickup_code(self, value):
        try:
            pickup = Pickup.objects.get(pickup_code=value)
            if pickup.status == 'COMPLETED':
                raise serializers.ValidationError("This QR code has already been used.")
            if pickup.is_expired:
                raise serializers.ValidationError("This QR code has expired.")
        except Pickup.DoesNotExist:
            raise serializers.ValidationError("Invalid QR code.")
        return value
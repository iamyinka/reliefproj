from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'id', 'reference_number', 'first_name', 'last_name', 'phone', 'email', 'address',
            'family_size', 'children_count', 'elderly_count', 'employment_status', 
            'special_needs', 'tec_member', 'selected_package', 'package_flexibility',
            'preferred_date', 'preferred_time', 'alternative_date', 'alternative_time',
            'transportation_help', 'delivery_request', 'terms_agreement', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'reference_number', 'status', 'created_at']


class ApplicationSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for anonymous application submission"""
    class Meta:
        model = Application
        fields = [
            'first_name', 'last_name', 'phone', 'email', 'address',
            'family_size', 'children_count', 'elderly_count', 'employment_status', 
            'special_needs', 'tec_member', 'selected_package', 'package_flexibility',
            'preferred_date', 'preferred_time', 'alternative_date', 'alternative_time',
            'transportation_help', 'delivery_request', 'terms_agreement'
        ]
    
    def validate_terms_agreement(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms and conditions.")
        return value
    
    def validate_phone(self, value):
        # Simple Nigerian phone number validation
        import re
        if not re.match(r'^(\+?234|0)[789][01]\d{8}$', value):
            raise serializers.ValidationError("Enter a valid Nigerian phone number.")
        return value
    
    def validate_tec_member(self, value):
        if value not in ['yes', 'no']:
            raise serializers.ValidationError("Please select your TEC membership status.")
        return value


class ApplicationReviewSerializer(serializers.ModelSerializer):
    """Serializer for supervisor application review"""
    class Meta:
        model = Application
        fields = ['id', 'reference_number', 'status', 'review_notes', 'reviewed_at']
        read_only_fields = ['id', 'reference_number', 'reviewed_at']
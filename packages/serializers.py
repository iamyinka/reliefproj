from rest_framework import serializers
from .models import Package, PackageItem


class PackageItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageItem
        fields = ['id', 'item_name', 'quantity', 'order']


class PackageSerializer(serializers.ModelSerializer):
    package_items = PackageItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'name', 'package_type', 'description', 'cash_amount', 
            'items_included', 'total_quantity', 'available_quantity', 
            'is_active', 'is_available', 'is_low_stock', 'package_items'
        ]
        read_only_fields = ['is_available', 'is_low_stock']


class PackageListSerializer(serializers.ModelSerializer):
    """Simplified serializer for package selection in forms"""
    class Meta:
        model = Package
        fields = ['package_type', 'name', 'description', 'cash_amount', 'is_available']
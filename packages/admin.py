from django.contrib import admin
from .models import Package, PackageItem


class PackageItemInline(admin.TabularInline):
    model = PackageItem
    extra = 3


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'package_type', 'cash_amount', 'available_quantity', 'is_active']
    list_filter = ['package_type', 'is_active']
    search_fields = ['name', 'description']
    inlines = [PackageItemInline]
    readonly_fields = ['created_at', 'updated_at']

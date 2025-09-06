from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'get_full_name', 'phone', 'selected_package', 
        'status', 'created_at'
    ]
    list_filter = ['status', 'selected_package', 'employment_status', 'created_at']
    search_fields = ['reference_number', 'first_name', 'last_name', 'phone', 'email']
    readonly_fields = ['reference_number', 'created_at', 'updated_at']
    fieldsets = [
        ('Personal Information', {
            'fields': ['reference_number', 'first_name', 'last_name', 'phone', 'email', 'address']
        }),
        ('Family Details', {
            'fields': ['family_size', 'children_count', 'elderly_count', 'employment_status', 
                      'special_needs', 'tec_member']
        }),
        ('Package Selection', {
            'fields': ['selected_package', 'package_flexibility']
        }),
        ('Pickup Schedule', {
            'fields': ['preferred_date', 'preferred_time', 'alternative_date', 'alternative_time',
                      'transportation_help', 'delivery_request']
        }),
        ('Status', {
            'fields': ['status', 'reviewed_by', 'reviewed_at', 'review_notes']
        }),
        ('System Info', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

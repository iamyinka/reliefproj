from django.contrib import admin
from .models import Pickup


@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ['pickup_code', 'get_applicant_name', 'scheduled_date', 'scheduled_time', 'status']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['pickup_code', 'application__first_name', 'application__last_name']
    readonly_fields = ['pickup_code', 'qr_code_image', 'created_at', 'updated_at']
    
    def get_applicant_name(self, obj):
        return obj.application.get_full_name()
    get_applicant_name.short_description = 'Applicant Name'

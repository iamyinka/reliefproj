from django.contrib import admin
from .models import DailyStats


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'applications_submitted', 'applications_approved', 
                    'packages_picked_up', 'total_cash_distributed']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']

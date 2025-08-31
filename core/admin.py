from django.contrib import admin
from .models import ConfigurationSettings, AuditLog


@admin.register(ConfigurationSettings)
class ConfigurationSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'is_active', 'updated_by', 'updated_at']
    list_filter = ['is_active', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'model_name', 'object_id']
    readonly_fields = ['created_at']

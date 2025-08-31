from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel


class Notification(TimeStampedModel):
    TYPE_CHOICES = [
        ('SMS', 'SMS'),
        ('EMAIL', 'Email'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]
    
    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    recipient = models.CharField(max_length=255)  # phone number or email
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} to {self.recipient} - {self.status}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel, ConfigurationSettings
import uuid


class Application(TimeStampedModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PICKED_UP', 'Picked Up'),
    ]
    
    # Unique identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Step 1: Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    
    # Step 2: Family Details
    family_size = models.CharField(max_length=10)
    children_count = models.CharField(max_length=10, default='0')
    elderly_count = models.CharField(max_length=10, default='0')
    employment_status = models.CharField(max_length=50)
    special_needs = models.TextField(blank=True)
    tec_member = models.CharField(
        max_length=3, 
        choices=[('yes', 'Yes'), ('no', 'No')],
        help_text='Member of The Elevation Church (TEC), Ibadan'
    )
    
    # Step 3: Package Selection
    selected_package = models.CharField(max_length=50)
    package_flexibility = models.BooleanField(default=False)
    
    # Step 4: Pickup Schedule
    preferred_date = models.DateField()
    preferred_time = models.CharField(max_length=20)
    alternative_date = models.DateField(null=True, blank=True)
    alternative_time = models.CharField(max_length=20, blank=True)
    transportation_help = models.BooleanField(default=False)
    delivery_request = models.BooleanField(default=False)
    
    # Step 5: Confirmation
    terms_agreement = models.BooleanField(default=False)
    
    # Application Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['phone']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.reference_number}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        from django.utils.crypto import get_random_string
        prefix = 'GCR'
        timestamp = timezone.now().strftime('%y%m')
        random_part = get_random_string(4, '0123456789')
        return f"{prefix}{timestamp}{random_part}"

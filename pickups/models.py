from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import TimeStampedModel
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid


class Pickup(TimeStampedModel):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    
    application = models.OneToOneField(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='pickup'
    )
    pickup_code = models.CharField(max_length=50, unique=True, blank=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True)
    
    scheduled_date = models.DateField()
    scheduled_time = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    # Pickup completion details
    picked_up_at = models.DateTimeField(null=True, blank=True)
    picked_up_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_pickups'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Pickup'
        verbose_name_plural = 'Pickups'
        ordering = ['scheduled_date', 'scheduled_time']
        indexes = [
            models.Index(fields=['pickup_code']),
            models.Index(fields=['scheduled_date', 'scheduled_time']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.application.get_full_name()} - {self.pickup_code}"
    
    def save(self, *args, **kwargs):
        if not self.pickup_code:
            self.pickup_code = self.generate_pickup_code()
        super().save(*args, **kwargs)
        if not self.qr_code_image:
            self.generate_qr_code()
    
    def generate_pickup_code(self):
        unique_id = str(uuid.uuid4()).replace('-', '').upper()[:12]
        return f"GCR{unique_id}"
    
    def generate_qr_code(self):
        qr_data = {
            'code': self.pickup_code,
            'application_id': str(self.application.id),
            'name': self.application.get_full_name(),
            'package': self.application.selected_package,
            'date': str(self.scheduled_date),
            'time': self.scheduled_time
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"qr_{self.pickup_code}.png"
        self.qr_code_image.save(filename, ContentFile(buffer.getvalue()), save=False)
        self.save(update_fields=['qr_code_image'])
    
    def complete_pickup(self, supervisor_user):
        self.status = 'COMPLETED'
        self.picked_up_at = timezone.now()
        self.picked_up_by = supervisor_user
        self.save()
        
        # Update application status
        self.application.status = 'PICKED_UP'
        self.application.save()
    
    @property
    def is_expired(self):
        # QR codes expire after 7 days or on scheduled date + 1 day
        expiry_date = max(
            self.scheduled_date + timezone.timedelta(days=1),
            self.created_at.date() + timezone.timedelta(days=7)
        )
        return timezone.now().date() > expiry_date

from django.db import models
from core.models import TimeStampedModel


class DailyStats(TimeStampedModel):
    date = models.DateField(unique=True)
    applications_submitted = models.PositiveIntegerField(default=0)
    applications_approved = models.PositiveIntegerField(default=0)
    applications_rejected = models.PositiveIntegerField(default=0)
    packages_picked_up = models.PositiveIntegerField(default=0)
    total_cash_distributed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Daily Statistics'
        verbose_name_plural = 'Daily Statistics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.date}"

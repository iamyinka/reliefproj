from django.db import models
from core.models import TimeStampedModel
from django.contrib.auth.models import User


class Package(TimeStampedModel):
    PACKAGE_TYPES = [
        ('small_basic', 'Small Family Basic'),
        ('medium_basic', 'Medium Family Basic'),
        ('emergency', 'Emergency Relief'),
        ('senior', 'Senior Citizen Special'),
    ]
    
    name = models.CharField(max_length=100)
    package_type = models.CharField(max_length=50, choices=PACKAGE_TYPES, unique=True)
    description = models.TextField()
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2)
    items_included = models.JSONField(
        help_text='JSON object with items and quantities (e.g., {"rice": "5kg", "beans": "2kg"})'
    )
    total_quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - ₦{self.cash_amount:,.0f}"
    
    @property
    def is_available(self):
        return self.is_active and self.available_quantity > 0
    
    @property
    def is_low_stock(self):
        threshold = 10  # Could be configurable
        return self.available_quantity <= threshold
    
    def allocate(self):
        if self.available_quantity > 0:
            self.available_quantity -= 1
            self.save()
            return True
        return False
    
    def restock(self, quantity):
        self.available_quantity += quantity
        self.total_quantity += quantity
        self.save()


class PackageItem(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='package_items')
    item_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)  # e.g., "5kg", "2L", "10 pieces"
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quantity} {self.item_name}"

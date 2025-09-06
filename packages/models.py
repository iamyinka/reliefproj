from django.db import models
from core.models import TimeStampedModel
from django.contrib.auth.models import User


class Package(TimeStampedModel):
    PACKAGE_TYPES = [
        ('small_basic', 'Small Family Basic'),
        ('small_premium', 'Small Family Premium'),
        ('medium_basic', 'Medium Family Basic'),
        ('medium_premium', 'Medium Family Premium'),
        ('large_basic', 'Large Family Basic'),
        ('large_premium', 'Large Family Premium'),
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
    
    @property
    def stock_status(self):
        """Return stock status for display"""
        if self.available_quantity == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'limited'
        else:
            return 'available'
    
    @property
    def stock_badge_class(self):
        """Return Bootstrap badge class for stock status"""
        status_classes = {
            'available': 'bg-success',
            'limited': 'bg-warning text-dark',
            'out_of_stock': 'bg-danger'
        }
        return status_classes.get(self.stock_status, 'bg-secondary')
    
    @property
    def stock_badge_text(self):
        """Return display text for stock status"""
        status_text = {
            'available': 'Available',
            'limited': 'Limited',
            'out_of_stock': 'Out of Stock'
        }
        return status_text.get(self.stock_status, 'Unknown')
    
    @property
    def family_size_category(self):
        """Return family size category for filtering"""
        if 'small' in self.package_type:
            return 'small'
        elif 'medium' in self.package_type:
            return 'medium'
        elif 'large' in self.package_type:
            return 'large'
        else:
            return 'all'
    
    @property
    def family_size_text(self):
        """Return family size description"""
        size_text = {
            'small': 'For families of 1-3 members',
            'medium': 'For families of 4-6 members', 
            'large': 'For families of 7+ members',
            'emergency': 'For urgent situations',
            'senior': 'For elderly members (60+)'
        }
        
        if 'emergency' in self.package_type:
            return size_text['emergency']
        elif 'senior' in self.package_type:
            return size_text['senior']
        else:
            return size_text.get(self.family_size_category, 'For all family sizes')
    
    @property
    def is_special_package(self):
        """Check if this is a special package (emergency or senior)"""
        return self.package_type in ['emergency', 'senior']
    
    @property
    def card_header_class(self):
        """Return header class for special packages"""
        if self.package_type == 'emergency':
            return 'bg-danger text-white'
        elif self.package_type == 'senior':
            return 'bg-success text-white'
        else:
            return ''
    
    @property
    def duration_text(self):
        """Return suitable duration text"""
        duration_map = {
            'small_basic': 'Suitable for 2-3 weeks',
            'small_premium': 'Suitable for 3-4 weeks',
            'medium_basic': 'Suitable for 2-3 weeks',
            'medium_premium': 'Suitable for 3-4 weeks',
            'large_basic': 'Suitable for 2-3 weeks',
            'large_premium': 'Suitable for 4-5 weeks',
            'emergency': 'Fast-tracked approval',
            'senior': 'Includes delivery service'
        }
        return duration_map.get(self.package_type, 'Duration varies')
    
    @property
    def duration_icon(self):
        """Return icon for duration text"""
        if self.package_type == 'emergency':
            return 'bi-lightning'
        elif self.package_type == 'senior':
            return 'bi-heart'
        else:
            return 'bi-clock'
    
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

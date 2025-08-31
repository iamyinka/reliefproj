from django.core.management.base import BaseCommand
from packages.models import Package, PackageItem


class Command(BaseCommand):
    help = 'Create sample packages for the relief program'

    def handle(self, *args, **options):
        # Clear existing packages
        Package.objects.all().delete()
        
        # Small Family Basic Package
        small_basic = Package.objects.create(
            name='Small Family Basic',
            package_type='small_basic',
            description='Basic relief package for small families (1-3 people)',
            cash_amount=5000.00,
            items_included={
                'rice': '5kg',
                'beans': '2kg',
                'oil': '1L',
                'salt': '500g'
            },
            total_quantity=50,
            available_quantity=50,
            is_active=True
        )
        
        PackageItem.objects.bulk_create([
            PackageItem(package=small_basic, item_name='Rice', quantity='5kg', order=1),
            PackageItem(package=small_basic, item_name='Beans', quantity='2kg', order=2),
            PackageItem(package=small_basic, item_name='Palm Oil', quantity='1L', order=3),
            PackageItem(package=small_basic, item_name='Salt', quantity='500g', order=4),
        ])
        
        # Medium Family Basic Package
        medium_basic = Package.objects.create(
            name='Medium Family Basic',
            package_type='medium_basic',
            description='Basic relief package for medium families (4-6 people)',
            cash_amount=8000.00,
            items_included={
                'rice': '10kg',
                'beans': '5kg',
                'oil': '2L',
                'salt': '1kg',
                'tomato_paste': '4 tins'
            },
            total_quantity=30,
            available_quantity=30,
            is_active=True
        )
        
        PackageItem.objects.bulk_create([
            PackageItem(package=medium_basic, item_name='Rice', quantity='10kg', order=1),
            PackageItem(package=medium_basic, item_name='Beans', quantity='5kg', order=2),
            PackageItem(package=medium_basic, item_name='Palm Oil', quantity='2L', order=3),
            PackageItem(package=medium_basic, item_name='Salt', quantity='1kg', order=4),
            PackageItem(package=medium_basic, item_name='Tomato Paste', quantity='4 tins', order=5),
        ])
        
        # Emergency Relief Package
        emergency = Package.objects.create(
            name='Emergency Relief',
            package_type='emergency',
            description='Fast-tracked relief for urgent situations',
            cash_amount=10000.00,
            items_included={
                'rice': '10kg',
                'beans': '3kg',
                'oil': '2L',
                'salt': '1kg',
                'maggi': '2 packs',
                'noodles': '5 packs'
            },
            total_quantity=20,
            available_quantity=20,
            is_active=True
        )
        
        PackageItem.objects.bulk_create([
            PackageItem(package=emergency, item_name='Rice', quantity='10kg', order=1),
            PackageItem(package=emergency, item_name='Beans', quantity='3kg', order=2),
            PackageItem(package=emergency, item_name='Palm Oil', quantity='2L', order=3),
            PackageItem(package=emergency, item_name='Salt', quantity='1kg', order=4),
            PackageItem(package=emergency, item_name='Maggi Cubes', quantity='2 packs', order=5),
            PackageItem(package=emergency, item_name='Instant Noodles', quantity='5 packs', order=6),
        ])
        
        # Senior Citizen Special Package
        senior = Package.objects.create(
            name='Senior Citizen Special',
            package_type='senior',
            description='Special package for elderly citizens with delivery service',
            cash_amount=6000.00,
            items_included={
                'rice': '5kg',
                'beans': '2kg',
                'oil': '1L',
                'milk': '2 tins',
                'oats': '1 pack'
            },
            total_quantity=25,
            available_quantity=25,
            is_active=True
        )
        
        PackageItem.objects.bulk_create([
            PackageItem(package=senior, item_name='Rice', quantity='5kg', order=1),
            PackageItem(package=senior, item_name='Beans', quantity='2kg', order=2),
            PackageItem(package=senior, item_name='Palm Oil', quantity='1L', order=3),
            PackageItem(package=senior, item_name='Powdered Milk', quantity='2 tins', order=4),
            PackageItem(package=senior, item_name='Oats', quantity='1 pack', order=5),
        ])
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created 4 sample packages:\n'
                f'- Small Family Basic: {small_basic.available_quantity} available\n'
                f'- Medium Family Basic: {medium_basic.available_quantity} available\n'
                f'- Emergency Relief: {emergency.available_quantity} available\n'
                f'- Senior Citizen Special: {senior.available_quantity} available'
            )
        )
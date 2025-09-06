from django.shortcuts import render
from packages.models import Package


def home(request):
    """Home page with featured packages"""
    # Get featured packages (available ones, limited to first 3)
    featured_packages = Package.objects.filter(
        is_active=True, 
        available_quantity__gt=0
    ).order_by('name')[:3]
    
    context = {
        'featured_packages': featured_packages
    }
    return render(request, 'pages/home.html', context)


def packages(request):
    """Packages listing page with all available packages"""
    packages = Package.objects.filter(is_active=True).order_by('name')
    
    context = {
        'packages': packages
    }
    return render(request, 'pages/packages.html', context)


def apply(request):
    """Application form page"""
    # Get available packages for the application form
    available_packages = Package.objects.filter(
        is_active=True,
        available_quantity__gt=0
    ).order_by('name')
    
    context = {
        'available_packages': available_packages
    }
    return render(request, 'pages/apply.html', context)


def status(request):
    """Application status checking page"""
    return render(request, 'pages/status.html')


def pickup(request):
    """Pickup details page"""
    return render(request, 'pages/pickup.html')

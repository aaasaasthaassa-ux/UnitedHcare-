from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Service, ServiceCategory
from .wishlist import Wishlist


def service_list(request, category_slug=None):
    """
    Display list of available services with filtering and search
    """
    services = Service.objects.filter(is_active=True).select_related('category')
    categories = ServiceCategory.objects.filter(is_active=True)
    
    # Filter by category
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(ServiceCategory, slug=category_slug, is_active=True)
        services = services.filter(category=selected_category)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    # Sort functionality
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'price_low':
        services = services.order_by('base_price')
    elif sort_by == 'price_high':
        services = services.order_by('-base_price')
    elif sort_by == 'popular':
        services = services.order_by('-total_bookings')
    else:  # featured (default)
        services = services.order_by('-is_featured', 'name')
    
    # Get wishlist items for logged-in users
    wishlist_service_ids = []
    if request.user.is_authenticated:
        wishlist_service_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('service_id', flat=True)
        )
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'sort_by': sort_by,
        'wishlist_service_ids': wishlist_service_ids,
    }
    
    return render(request, 'services/service_list.html', context)


def service_detail(request, slug):
    """
    Display detailed information about a specific service
    """
    service = get_object_or_404(
        Service.objects.select_related('category'), 
        slug=slug, 
        is_active=True
    )
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(
            user=request.user, 
            service=service
        ).exists()
    
    # Get related services
    related_services = Service.objects.filter(
        category=service.category,
        is_active=True
    ).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'in_wishlist': in_wishlist,
        'related_services': related_services,
    }
    
    return render(request, 'services/service_detail.html', context)


@login_required
def add_to_wishlist(request, service_id):
    """
    Add a service to user's wishlist
    """
    service = get_object_or_404(Service, id=service_id, is_active=True)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        service=service
    )
    
    if created:
        messages.success(request, f'{service.name} added to your wishlist.')
    else:
        messages.info(request, f'{service.name} is already in your wishlist.')
    
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'services:list'))


@login_required
def remove_from_wishlist(request, service_id):
    """
    Remove a service from user's wishlist
    """
    service = get_object_or_404(Service, id=service_id)
    
    deleted_count, _ = Wishlist.objects.filter(
        user=request.user,
        service=service
    ).delete()
    
    if deleted_count > 0:
        messages.success(request, f'{service.name} removed from your wishlist.')
    else:
        messages.error(request, 'Service not found in your wishlist.')
    
    return redirect(request.META.get('HTTP_REFERER', 'services:list'))


@login_required
def wishlist_view(request):
    """
    Display user's wishlist
    """
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('service', 'service__category').order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'services/wishlist.html', context)
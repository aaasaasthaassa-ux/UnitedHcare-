from decimal import Decimal


def cart_and_wishlist_counts(request):
    """Return counts for cart and wishlist to be used in templates.

    Provides:
    - cart_count: number of items in the user's pharmacy cart
    - wishlist_count: combined wishlist count across pharmacy, services and equipment where available
    """
    cart_count = 0
    wishlist_count = 0

    if not request.user.is_authenticated:
        return {
            'cart_count': 0,
            'wishlist_count': 0,
        }

    try:
        from .models import Cart, PharmacyWishlist
        cart = Cart.objects.filter(user=request.user, cart_type='pharmacy').first()
        cart_count = cart.total_items if cart else 0
    except Exception:
        cart_count = 0

    # Pharmacy wishlist
    try:
        from .models import PharmacyWishlist
        wishlist_count += PharmacyWishlist.objects.filter(user=request.user).count()
    except Exception:
        pass

    # Services wishlist (optional)
    try:
        from apps.services.models import Wishlist as ServiceWishlist
        wishlist_count += ServiceWishlist.objects.filter(user=request.user).count()
    except Exception:
        pass

    # Equipment wishlist (optional)
    try:
        from apps.equipment.models import EquipmentWishlist
        wishlist_count += EquipmentWishlist.objects.filter(user=request.user).count()
    except Exception:
        pass

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }

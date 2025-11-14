"""
Compatibility shim: expose Wishlist from `apps.services.models`.

This file remains so older imports like `from apps.services.wishlist import Wishlist`
continue to work while the canonical model lives in `apps.services.models`.
"""

from .models import Wishlist  # noqa: F401
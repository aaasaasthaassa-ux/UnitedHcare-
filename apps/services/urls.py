from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Service listing
    path('', views.service_list, name='list'),
    path('category/<slug:category_slug>/', views.service_list, name='list_by_category'),
    
    # Wishlist (placed before the slug-based detail route to avoid being captured)
    path('wishlist/add/<int:service_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:service_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),

    # Service detail (slug route should come after explicit routes)
    path('<slug:slug>/', views.service_detail, name='detail'),
]
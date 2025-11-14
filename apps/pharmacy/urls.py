from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    # Medicine browsing
    path('', views.medicine_list, name='list'),
    path('category/<slug:category_slug>/', views.medicine_list, name='list_by_category'),
    path('medicine/<slug:slug>/', views.medicine_detail, name='detail'),
    
    # Cart
    path('cart/', views.pharmacy_cart, name='cart'),
    path('cart/add/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('order/<str:order_number>/cancel/', views.cancel_order, name='cancel_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
]

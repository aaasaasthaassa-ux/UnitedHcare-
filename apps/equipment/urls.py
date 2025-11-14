from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    # Equipment browsing
    path('', views.equipment_list, name='list'),
    path('category/<slug:category_slug>/', views.equipment_list, name='list_by_category'),
    # Rent & Buy
    path('rent/<int:equipment_id>/', views.rent_equipment, name='rent'),
    path('buy/<int:equipment_id>/', views.buy_equipment, name='buy'),

    # My Rentals & Purchases
    path('my-rentals/', views.my_rentals, name='my_rentals'),
    path('my-purchases/', views.my_purchases, name='my_purchases'),

    # Order detail pages
    path('purchase/<str:order_number>/', views.purchase_detail, name='purchase_detail'),
    path('purchase/<str:order_number>/cancel/', views.cancel_purchase, name='cancel_purchase'),
    path('rental/<str:rental_number>/', views.rental_detail, name='rental_detail'),
    path('rental/<str:rental_number>/cancel/', views.cancel_rental, name='cancel_rental'),
    path('rental/<str:rental_number>/return/', views.return_rental, name='return_rental'),

    # Detail (slug) must come last to avoid catching other literal paths
    path('<slug:slug>/', views.equipment_detail, name='detail'),
]

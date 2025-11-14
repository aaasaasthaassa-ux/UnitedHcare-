from django.urls import path
from . import views
from . import personal_views

app_name = 'appointments'

urlpatterns = [
    # Book appointment
    path('book/<int:service_id>/', views.book_appointment, name='book'),
    path('confirm/<int:appointment_id>/', views.appointment_confirmation, name='confirmation'),
    
    # Manage appointments
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('detail/<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel'),
    
    # Provider actions
    path('provider/pending/', views.provider_pending_appointments, name='provider_pending'),
    path('provider/accept/<int:appointment_id>/', views.accept_appointment, name='accept'),
    path('provider/reject/<int:appointment_id>/', views.reject_appointment, name='reject'),
    path('provider/complete/<int:appointment_id>/', views.complete_appointment, name='complete'),
]

# Personal appointments (direct patient-provider bookings)
urlpatterns += [
    path('providers/', personal_views.provider_directory, name='provider_directory'),
    path('provider/<int:provider_id>/', personal_views.provider_detail, name='provider_detail'),
    path('provider/<int:provider_id>/book/', personal_views.book_personal_appointment, name='book_personal_appointment'),
    path('provider/<int:provider_id>/slots/<str:date>/', personal_views.get_available_slots, name='get_available_slots'),

    # My Personal Appointments
    path('personal/', personal_views.my_personal_appointments, name='my_personal_appointments'),
    path('personal/<int:appointment_id>/', personal_views.personal_appointment_detail, name='personal_appointment_detail'),
    path('personal/<int:appointment_id>/confirm/', personal_views.confirm_personal_appointment, name='confirm_personal_appointment'),
    path('personal/<int:appointment_id>/complete/', personal_views.complete_personal_appointment, name='complete_personal_appointment'),
    path('personal/<int:appointment_id>/cancel/', personal_views.cancel_personal_appointment, name='cancel_personal_appointment'),
    path('personal/<int:appointment_id>/review/', personal_views.add_appointment_review, name='add_appointment_review'),
]
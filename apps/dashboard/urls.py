from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard (role-based routing)
    path('', views.dashboard_home, name='home'),
    
    # Patient dashboard
    path('patient/', views.patient_dashboard, name='patient'),
    path('patient/balance/', views.patient_balance, name='patient_balance'),
    
    # Provider dashboard
    path('provider/', views.provider_dashboard, name='provider'),
    path('provider/schedule/', views.provider_schedule, name='provider_schedule'),
    
    # Admin dashboard
    path('admin/', views.admin_dashboard, name='admin'),
]
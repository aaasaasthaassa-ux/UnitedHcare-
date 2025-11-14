from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Registration
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/provider/', views.register_provider, name='register_provider'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    # Password change (using Django's built-in view)
    path(
        'password/change/',
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/password_change.html',
            success_url=reverse_lazy('accounts:password_change_done')
        ),
        name='change_password'
    ),
    path(
        'password/change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='accounts/password_change_done.html'
        ),
        name='password_change_done'
    ),
]
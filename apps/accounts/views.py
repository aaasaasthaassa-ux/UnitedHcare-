from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import (
    PatientRegistrationForm, 
    ProviderRegistrationForm, 
    LoginForm,
    ProfileUpdateForm
)
from .models import User, PatientProfile, ProviderProfile
from decimal import Decimal
from django.contrib.auth.views import PasswordResetView
from django.core.mail import mail_admins
from django.utils import timezone


class PasswordResetNotifyView(PasswordResetView):
    """PasswordResetView that notifies site admins when a reset is requested.

    It calls the normal password-reset workflow and additionally sends a
    short notification to the addresses configured in settings.ADMINS using
    django.core.mail.mail_admins(). Ensure ADMINS is set in settings for
    production use; in DEBUG the console email backend will capture output.
    """

    def form_valid(self, form):
        # Gather contextual info to include in the admin notification
        request = self.request
        email = form.cleaned_data.get('email')
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        ua = request.META.get('HTTP_USER_AGENT', '')
        subject = f"Password reset requested for {email}"
        message = (
            f"A password reset was requested on {request.get_host()}\n"
            f"Time: {timezone.now().isoformat()}\n"
            f"Email entered: {email}\n"
            f"IP address: {ip}\n"
            f"User-Agent: {ua}\n"
            f"Path: {request.path}\n"
        )
        try:
            # mail_admins uses the ADMINS setting; in DEBUG it will go to console
            mail_admins(subject, message, fail_silently=True)
        except Exception:
            # Silently ignore notification failures to avoid breaking the user flow
            pass

        return super().form_valid(form)


def about(request):
    """About Us static page"""
    return render(request, 'about.html')


def contact(request):
    """Contact Us static page with a simple contact form (placeholder).

    For now this renders contact information and a simple contact form that
    posts nowhere (can be hooked up to email or ticketing later).
    """
    return render(request, 'contact.html')


def register_patient(request):
    """
    Patient registration view
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user
                    user = form.save(commit=False)
                    user.role = 'patient'
                    user.save()

                    # Create patient profile
                    PatientProfile.objects.create(
                        user=user,
                        medical_history=form.cleaned_data.get('medical_history', ''),
                        blood_group=form.cleaned_data.get('blood_group', '')
                    )
                # End transaction before logging in to avoid session DB conflicts

                # Authenticate the newly created user so the backend attribute
                # is set (required when multiple authentication backends are
                # configured). Fall back to setting `backend` on the user
                # if authenticate() fails for any reason.
                password = form.cleaned_data.get('password1')
                auth_user = authenticate(request, username=user.username, password=password)

                if auth_user is not None:
                    login(request, auth_user)
                else:
                    # As a fallback, set the backend to the first configured
                    # authentication backend so login() can proceed.
                    backend = None
                    try:
                        backend = settings.AUTHENTICATION_BACKENDS[0]
                    except Exception:
                        backend = 'django.contrib.auth.backends.ModelBackend'
                    user.backend = backend
                    login(request, user)
                messages.success(request, 'Welcome to UH Care! Your account has been created successfully.')

                # Support optional `next` parameter to redirect after registration
                next_param = request.POST.get('next') or request.GET.get('next')
                if next_param and url_has_allowed_host_and_scheme(next_param, allowed_hosts={request.get_host()}):
                    return redirect(next_param)
                return redirect('dashboard:home')
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'accounts/register_patient.html', {'form': form})


def register_provider(request):
    """
    Healthcare provider registration view
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user
                    user = form.save(commit=False)
                    user.role = 'provider'
                    user.is_active = False  # Require admin approval
                    user.save()
                    
                    # Create provider profile
                    ProviderProfile.objects.create(
                        user=user,
                        specialization=form.cleaned_data.get('specialization'),
                        license_number=form.cleaned_data.get('license_number'),
                        years_of_experience=form.cleaned_data.get('years_of_experience', 0),
                        bio=form.cleaned_data.get('bio', ''),
                        hourly_rate=form.cleaned_data.get('hourly_rate', 500.00)
                    )
                    
                    messages.success(
                        request, 
                        'Your provider account has been submitted for approval. We will notify you once approved.'
                    )
                    return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProviderRegistrationForm()
    
    return render(request, 'accounts/register_provider.html', {'form': form})


def user_login(request):
    """
    User login view (both patients and providers)
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('identifier')
            password = form.cleaned_data.get('password')

            # Authenticate using custom backend (username or email)
            user = authenticate(request, username=identifier, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')

                    # Redirect safely. Support `next` coming from GET or POST.
                    next_param = request.POST.get('next') or request.GET.get('next')
                    if next_param and url_has_allowed_host_and_scheme(next_param, allowed_hosts={request.get_host()}):
                        return redirect(next_param)
                    return redirect('dashboard:home')
                else:
                    messages.error(request, 'Your account is pending approval. Please wait for admin verification.')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    # Redirect to the site homepage. The accounts app provides this at the
    # namespaced URL 'accounts:home' (included at the root URLconf), so use
    # the namespaced name to avoid NoReverseMatch.
    return redirect('accounts:home')


@login_required
def profile_view(request):
    """
    View and update user profile
    """
    user = request.user
    
    # Get the appropriate profile
    profile = None
    if user.role == 'patient':
        try:
            profile = user.patient_profile
        except Exception:
            profile, _ = PatientProfile.objects.get_or_create(
                user=user,
                defaults={
                    'medical_history': '',
                    'blood_group': '',
                    'total_balance': Decimal('0.00')
                }
            )
    elif user.role == 'provider':
        try:
            profile = user.provider_profile
        except Exception:
            temp_license = f"pending-{user.id}-{int(timezone.now().timestamp())}"
            profile, _ = ProviderProfile.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': ProviderProfile.SPECIALIZATION_CHOICES[0][0],
                    'license_number': temp_license,
                    'years_of_experience': 0,
                    'bio': '',
                    'hourly_rate': Decimal('500.00'),
                    'is_available': False,
                }
            )
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user, user_role=user.role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=user, user_role=user.role)
    
    context = {
        'form': form,
        'profile': profile,
        'user': user
    }
    
    return render(request, 'accounts/profile.html', context)


def home(request):
    """
    Homepage view
    Show a small curated set of items from services, equipment, and recent
    pharmacy orders so the home page feels alive with real data.
    If the user is authenticated we still redirect them to the dashboard
    to avoid duplicating the logged-in UX.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    # Lazy imports so apps without models won't break this view during tests
    services = []
    equipments = []
    recent_pharmacy_orders = []

    try:
        from apps.services.models import Service
        services = list(Service.objects.filter(is_active=True).order_by('-is_featured', 'name')[:3])
    except Exception:
        services = []

    try:
        from apps.equipment.models import Equipment
        equipments = list(Equipment.objects.filter(is_active=True).order_by('-available_units')[:3])
    except Exception:
        equipments = []

    try:
        from apps.pharmacy.models import Medicine
        # show featured medicines first, then any active medicines
        pharmacy_products = list(Medicine.objects.filter(is_active=True).order_by('-is_featured', 'name')[:6])
    except Exception:
        pharmacy_products = []

    context = {
        'services': services,
        'equipments': equipments,
        'pharmacy_products': pharmacy_products,
    }

    return render(request, 'home.html', context)
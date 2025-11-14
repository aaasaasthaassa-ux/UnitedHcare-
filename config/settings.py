from pathlib import Path
import os
try:
    import dj_database_url
except Exception:
    dj_database_url = None

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# Hosts
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,testserver').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Project apps
    'apps.accounts',
    'apps.services',
    'apps.appointments',
    'apps.payments',
    'apps.notifications',
    'apps.equipment',
    'apps.pharmacy',
    'apps.dashboard',
    # Content: Blog
    'apps.blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise should come right after SecurityMiddleware to efficiently serve static files in production
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Cart and wishlist counts available in all templates
                'apps.pharmacy.context_processors.cart_and_wishlist_counts',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Database configuration: support DATABASE_URL env var (Postgres) and
# fallback to SQLite for local development.
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and dj_database_url is not None:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Allow authentication by username or email using a custom backend
AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# Use leading slashes so generated URLs are absolute (important for correct
# resolution of static and media resources in templates and when served by
# development server or WhiteNoise).
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
# Use a leading slash so media URLs resolve from site root (e.g. /media/...) 
# instead of relative paths which can break when visiting nested pages like /services/.
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Default model for AI/LLM calls from the app. Set via environment variable
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gpt-5-mini')

# Helper: You can reference settings.DEFAULT_MODEL wherever you build API calls

# Payment defaults used by the payments app when generating/displaying QR codes
PAYMENT_QR_CODE_URL = os.getenv('PAYMENT_QR_CODE_URL', '')
PAYMENT_ACCOUNT_NAME = os.getenv('PAYMENT_ACCOUNT_NAME', 'UH Care')
PAYMENT_ACCOUNT_NUMBER = os.getenv('PAYMENT_ACCOUNT_NUMBER', '0000-0000-0000')

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'redis://redis:6379/0'))
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)

# AWS S3 / storage settings (optional)
USE_S3 = os.getenv('USE_S3', 'False') == 'True'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', '')
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN', '')

if USE_S3 and AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # Optionally use S3 for static files in production
    STATICFILES_STORAGE = os.getenv('STATICFILES_STORAGE', 'storages.backends.s3boto3.S3Boto3Storage')
else:
    # Local file storage defaults (dev)
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    # When not using S3, use WhiteNoise's compressed manifest storage in production for
    # efficient static file serving. This requires `whitenoise` in requirements (already present).
    if not USE_S3:
        STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # -----------------------
    # Email configuration
    # -----------------------
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@uhcare.com.np')

    # Development-friendly override: when running with DEBUG enabled,
    # use the console email backend so that password reset and other
    # email-sending views don't attempt an external SMTP connection
    # (which can fail with SSL cert validation errors on local machines).
    if DEBUG:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # -----------------------
    # Twilio / SMS configuration (optional)
    # -----------------------
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
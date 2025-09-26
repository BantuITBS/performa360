import os
from pathlib import Path

# Path settings
BASE_DIR = Path(__file__).resolve().parent.parent

# Security and general settings
SECRET_KEY = 'django-insecure-43a7i-yjqn=s6@ezgq1wzeq@v#ol_9i1unlr_7krkdv8#rlq_z'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
APPEND_SLASH = False

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8002",
    "http://localhost:8002",
]
CORS_ALLOW_CREDENTIALS = True  # Allow cookies to be sent with requests

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8002",
    "http://localhost:8002",
]

# Custom User Model
AUTH_USER_MODEL = 'perf_mgmt.UserCreationModel'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',  # For additional Django management commands
    'rest_framework',     # For Django REST Framework
    'corsheaders',        # For CORS handling
    'perf_mgmt',          # Your app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_COOKIE_AGE = 3600  # 1 hour

ROOT_URLCONF = 'perf_mgmt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'perf_mgmt.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'performa360',
        'USER': 'takawira',
        'PASSWORD': 'MAZAtaka@45',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static Files Configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'perf_mgmt', 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization & Time Zone
TIME_ZONE = 'Africa/Johannesburg'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session settings
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True

# Login URL
LOGIN_URL = '/login/'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.db.backends': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'perf_mgmt': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}

# OpenAI integration
OPENAI_API_KEY = "sk-..."  # Replace with your real key

# ---- Optional: Install required packages if missing ----
# These should be installed in your virtual environment
# pip install django django_extensions djangorestframework corsheaders phonenumbers spacy openai pillow mysqlclient python-decouple

# SpaCy model note: Load en_core_web_md in your code after installation:
# import spacy
# nlp = spacy.load("en_core_web_md")

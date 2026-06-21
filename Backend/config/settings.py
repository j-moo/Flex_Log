from datetime import timedelta
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-flex-log-development-key-change-me-2026',
)
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'accounts',
    'profiles',
    'friends',
    'expenses',
    'analysis',
    'finance',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174',
    ).split(',')
    if origin.strip()
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^http://localhost:517\d$',
    r'^http://127\.0\.0\.1:517\d$',
]

GMS_KEY = os.getenv('GMS_KEY')
GMS_API_URL = os.getenv(
    'GMS_API_URL',
    'https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions',
)
GMS_MODEL = os.getenv('GMS_MODEL', 'gpt-5.4-nano')

FINLIFE_API_KEY = os.getenv('api_key') or os.getenv('FINLIFE_API_KEY')
FINLIFE_API_BASE_URL = os.getenv(
    'FINLIFE_API_BASE_URL',
    'https://finlife.fss.or.kr/finlifeapi',
)
FINLIFE_TOP_FIN_GRP_NO = os.getenv('FINLIFE_TOP_FIN_GRP_NO', '020000')

KIWOOM_APP_KEY = os.getenv('KIWOOM_APP_KEY') or os.getenv('KIWOOM_API_KEY')
KIWOOM_SECRET_KEY = os.getenv('KIWOOM_SECRET_KEY') or os.getenv('KIWOOM_API_SECRET')
KIWOOM_BASE_URL = os.getenv('KIWOOM_BASE_URL', 'https://api.kiwoom.com')
KIWOOM_TOKEN_PATH = os.getenv('KIWOOM_TOKEN_PATH', '/oauth2/token')
KIWOOM_REQUEST_TIMEOUT = int(os.getenv('KIWOOM_REQUEST_TIMEOUT', '10'))

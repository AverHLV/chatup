from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from os import environ
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_DB_URL = 'postgres://postgres:postgres@localhost:5432/chatup'
DEFAULT_REDIS_URL = 'redis://localhost:6379'
DEFAULT_HOST = 'http://127.0.0.1:8000'
DEBUG_SECRET_KEY = 'secret'

BASE_DIR = Path(__file__).resolve().parent.parent

# General

SECRET_KEY = environ.get('CH_SECRET_KEY', DEBUG_SECRET_KEY)

DEBUG = environ.get('CH_DEBUG', 'true') == 'true'

if not DEBUG and SECRET_KEY == DEBUG_SECRET_KEY:
    raise ImproperlyConfigured('Debug mode disabled but default secret key used')

ALLOWED_HOSTS = environ.get('CH_ALLOWED_HOSTS', '*').split(',')

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Authentication

AUTH_USER_MODEL = 'chat.User'

# Application definition

INSTALLED_APPS = [
    # use whitenoise serving on development

    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_yasg',
    'channels',

    # own apps

    'api.chat',
    'api.auth_api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
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

# Database

db_url = urlparse(environ.get('DATABASE_URL', DEFAULT_DB_URL))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_url.path[1:],
        'USER': db_url.username,
        'PASSWORD': db_url.password,
        'HOST': db_url.hostname,
        'PORT': db_url.port,
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

# Cache

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': environ.get('REDIS_URL', DEFAULT_REDIS_URL),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 3600 * 12

# REST API

REST_API_HOST = urlparse(environ.get('CH_HOST', DEFAULT_HOST))
REST_API_USE_HTTPS = REST_API_HOST.scheme == 'https'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

if REST_API_USE_HTTPS:
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.abstract.pagination.CustomLimitOffsetPagination',
    'EXCEPTION_HANDLER': 'api.abstract.exception_handler.custom_exception_handler',
    'PAGE_SIZE': 30,

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )

# Channels

ASGI_APPLICATION = 'config.routing.router'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [environ.get('REDIS_URL', DEFAULT_REDIS_URL)],
        },
    },
}

# Logging configuration

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'formatter': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },

        'handlers': {
            'file_handler': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'chatup.log',
                'formatter': 'formatter',
                'maxBytes': 10485760,  # 10 MB
            },
        },

        'loggers': {
            'django': {
                'handlers': ['file_handler'],
                'level': 'INFO',
                'propagate': True,
            },
        }
    }

# Fixtures

FIXTURE_DIRS = BASE_DIR / 'fixtures',

# Internationalization

LOCALE_PATHS = BASE_DIR / 'locales',

# First tuple determines a default field translation language code in the translation mixins

LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)

default_lang = environ.get('CH_DEFAULT_LANG', 'en')
if default_lang not in (lang[0] for lang in LANGUAGES):
    raise ImproperlyConfigured(f'Specified default language not supported: {default_lang}')

LANGUAGE_CODE = default_lang

LANGUAGE_COOKIE_NAME = 'lang'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = BASE_DIR / 'ui',

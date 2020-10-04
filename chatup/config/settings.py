from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from os import environ
from pathlib import Path
from configparser import ConfigParser

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / 'config' / environ.get('CUP_CONF', 'config.ini')

if not CONFIG_PATH.is_file():
    raise ImproperlyConfigured(f'Config file with specified path not found: {CONFIG_PATH}')

config = ConfigParser()
config.read(CONFIG_PATH)

# General

SECRET_KEY = config.get('django', 'secret_key')

DEBUG = True if config.get('django', 'debug', fallback='true') == 'true' else False

ALLOWED_HOSTS = config.get('django', 'hosts').split()

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Authentication

AUTH_USER_MODEL = 'chat.CustomUser'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',

    # own apps

    'apps.chat',
    'apps.auth_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config.get('database', 'name'),
        'USER': config.get('database', 'user'),
        'PASSWORD': config.get('database', 'password'),
        'HOST': config.get('database', 'host'),
        'PORT': config.get('database', 'port'),

        'TEST': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config.get('database_test', 'name'),
            'USER': config.get('database_test', 'user'),
            'PASSWORD': config.get('database_test', 'password'),
            'HOST': config.get('database_test', 'host'),
            'PORT': config.get('database_test', 'port'),
        }
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

if config.get('cache', 'user', fallback=None) is None:
    location = f'redis://{config.get("cache", "host")}:{config.get("cache", "port")}/0'

else:
    user = config.get('cache', 'user')
    password = config.get('cache', 'password')
    host = config.get('cache', 'host')
    port = config.get('cache', 'port')

    location = f'redis://{user}:{password}@{host}:{port}/0'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': location,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 3600 * 12

# REST API

REST_API_VERSION = 'v1'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'apps.pagination.CustomLimitOffsetPagination',
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

default_lang = config.get('django', 'default_lang', fallback='en')

if default_lang not in [lang[0] for lang in LANGUAGES]:
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

CORS_ORIGIN_ALLOW_ALL = True

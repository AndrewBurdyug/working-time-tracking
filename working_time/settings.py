import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# WARNING: override by the local_settings.py
# SECRET_KEY = ''

# WARNING: override by the local_settings.py
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False

# WARNING: override by the local_settings.py
# ALLOWED_HOSTS = []


# Application definition

ADDONS = (
    'cacheops',
)

APPS = (
    'timesheet',
)

INSTALLED_APPS = (
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
) + ADDONS + APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'working_time.urls'

WSGI_APPLICATION = 'working_time.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

# WARNING: override by the local_settings.py
# TIME_ZONE = ''

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Project folders:

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': False,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )

REPORTS_DIR = os.path.join(MEDIA_ROOT, 'reports')

INVOICES_DIR = os.path.join(MEDIA_ROOT, 'invoices')


# Cacheops settings:

CACHEOPS_REDIS = {
    'db': 3,
    # 'unix_socket_path': '/tmp/redis.sock'
}

CACHEOPS_DEFAULTS = {
    'timeout': 60 * 60
}

CACHEOPS = {
    'timesheet.*': {'ops': 'all'},
    'auth.*': {'ops': 'all'},
}


# Override the default settings:

from local_settings import *

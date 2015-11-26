"""
Django settings for genequery project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from genequery.utils import here

LOCAL_APPS = ()

try:
    from local_settings import *
except ImportError:
    pass


SECRET_KEY = 'n%d(+weua8k&w58i%&$xe_$4ax84(gw*%j9wqu)vk@&(n=1m^%'

# TEMPLATES
TEMPLATE_DEBUG = True
TEMPLATE_DIRS = (
    BASE_DIR + 'templates/',
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Application definition

TEST_RUNNER = 'utils.test.GQTestRunner'

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

PROJECT_APPS = (
    'genequery.searcher',
    'genequery.main',
)

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'genequery.urls'

WSGI_APPLICATION = 'genequery.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(name)s %(asctime)s %(module)s.py, line %(lineno)d, in %(funcName)s:\t%(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
        'rpc_verbose': {
            'format': '%(levelname)s %(name)s %(asctime)s %(module)s:%(lineno)d\tthread-%(thread)d\tprocess-%(process)d\t%(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'common_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': here(LOG_DIR, 'genequery.log'),
            'maxBytes': 1024 * 1024 * 30,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'rpc_stats_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': here(LOG_DIR, 'rpc_stats.log'),
            'maxBytes': 1024 * 1024 * 30,
            'backupCount': 10,
            'formatter': 'rpc_verbose',
        },
    },
    'loggers': {
        'genequery': {
            'handlers': ['console', 'common_file'],
            'level': 'DEBUG',
        },
        'rpc': {
            'handlers': ['console', 'rpc_stats_file'],
            'level': 'DEBUG',
        },
    }
}
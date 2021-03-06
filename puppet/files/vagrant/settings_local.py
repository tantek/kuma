from settings import *
import logging

INTERNAL_IPS = ('127.0.0.1', '192.168.10.1',)

DEBUG = True
DEV = True
TEMPLATE_DEBUG = DEBUG
SERVE_MEDIA = DEBUG

SESSION_COOKIE_SECURE = False

DEMO_UPLOADS_ROOT = '/home/vagrant/uploads/demos'
DEMO_UPLOADS_URL = '/media/uploads/demos/'

PROD_DETAILS_DIR = '/home/vagrant/product_details_json'
MDC_PAGES_DIR    = '/home/vagrant/mdc_pages'

DEKIWIKI_ENDPOINT = "http://localhost"

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6LdX8cISAAAAAA9HRXmzrcRSFsUoIK9u0nWpvGS_'
RECAPTCHA_PRIVATE_KEY = '6LdX8cISAAAAACkC1kqYmpeSf-1geTmLzrLnq0t6'

BITLY_USERNAME = 'lmorchard'
BITLY_API_KEY = "R_2653e6351e31d02988b3da31dac6e2c0"

INSTALLED_APPS = INSTALLED_APPS + (
    "django_extensions",
    "debug_toolbar",
    "devserver",
)

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    #'cache_panel.CachePanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

# The default database should point to the master.
DATABASES = {
    'default': {
        'NAME': 'kuma',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'USER': 'kuma',
        'PASSWORD': 'kuma',
        'OPTIONS': {'init_command': 'SET storage_engine=InnoDB'},
    },
}

# Use IP:PORT pairs separated by semicolons.
CACHE_BACKEND = 'django_pylibmc.memcached://localhost:11211?timeout=3600'
CONSTANCE_DATABASE_CACHE_BACKEND = CACHE_BACKEND

# This is used to hash some things in Django.
SECRET_KEY = 'jenny8675309'

DEBUG_PROPAGATE_EXCEPTIONS = DEBUG

LOG_LEVEL = logging.DEBUG
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = '/home/vagrant/logs/kuma-django.log',
)

SPHINX_INDEXER = '/usr/local/bin/indexer'
SPHINX_SEARCHD = '/usr/local/bin/searchd'
SEARCH_CACHE_PERIOD = 0 

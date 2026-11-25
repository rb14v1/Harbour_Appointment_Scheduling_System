import sys
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
# Load a local .env file (if present) for development; real environment variables win.
environ.Env.read_env(BASE_DIR / ".env")

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

REQUIRED_ENV_VARS = [
    "DJANGO_SECRET_KEY",
    "DJANGO_DEBUG",
    "DJANGO_ALLOWED_HOSTS",
    "MONGO_URI",
    "MONGO_DB_NAME",
]
_missing = [name for name in REQUIRED_ENV_VARS if not env.str(name, default="").strip()]
if _missing:
    raise ImproperlyConfigured(
        "Missing required environment variables: " + ", ".join(_missing)
    )

SECRET_KEY = env.str("DJANGO_SECRET_KEY")
DEBUG = env.str("DJANGO_DEBUG").strip() == "1"
ALLOWED_HOSTS = [
    host.strip()
    for host in env.str("DJANGO_ALLOWED_HOSTS").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "rest_framework",
    "appointments",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = []

# Application data lives in MongoDB (PyMongo). No relational database is used.
DATABASES = {}

USE_TZ = True
TIME_ZONE = env.str("APP_TIME_ZONE", default="UTC")

MONGO_URI = env.str("MONGO_URI")
if TESTING:
    MONGO_DB_NAME = env.str("MONGO_TEST_DB_NAME", default=env.str("MONGO_DB_NAME") + "_test")
else:
    MONGO_DB_NAME = env.str("MONGO_DB_NAME")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
    "EXCEPTION_HANDLER": "appointments.exceptions.custom_exception_handler",
}

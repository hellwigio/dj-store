import os

os.environ["DJANGO_READ_DOT_ENV"] = "false"
os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-key-never-use-in-production")
os.environ["DATABASE_URL"] = "sqlite://:memory:"

from .base import *  # noqa: E402

ALLOWED_HOSTS = ["testserver", "localhost"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

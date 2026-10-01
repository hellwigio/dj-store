from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extend here before the first production deployment."""

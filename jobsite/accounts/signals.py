from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Keep this signal idempotent and side-effect free: ensure a Profile exists,
    # but do not attempt to resave it (that can conflict with role-lock logic).
    Profile.objects.get_or_create(user=instance)

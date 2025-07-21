from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import SkinProfile

@receiver(post_save, sender=User)
def create_skin_profile(sender, instance, created, **kwargs):
    if created:
        SkinProfile.objects.create(user=instance)

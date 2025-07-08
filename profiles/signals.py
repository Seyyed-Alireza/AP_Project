from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


import os
from django.db.models.signals import pre_save, post_delete

@receiver(pre_save, sender=UserProfile)
def delete_old_profile_picture(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        return

    old_file = old_instance.profile_picture
    new_file = instance.profile_picture

    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path) and 'default' not in old_file.name:
            os.remove(old_file.path)

@receiver(post_delete, sender=UserProfile)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    if instance.profile_picture and os.path.isfile(instance.profile_picture.path):
        if 'default' not in instance.profile_picture.name:
            os.remove(instance.profile_picture.path)
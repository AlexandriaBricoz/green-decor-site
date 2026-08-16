from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Plant


def _delete_file(fieldfile):
    if fieldfile and fieldfile.name:
        fieldfile.storage.delete(fieldfile.name)


@receiver(post_delete, sender=Plant)
def plant_delete_photo(sender, instance, **kwargs):
    _delete_file(instance.photo)


@receiver(pre_save, sender=Plant)
def plant_replace_photo(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Plant.objects.get(pk=instance.pk)
    except Plant.DoesNotExist:
        return
    if old.photo and old.photo != instance.photo:
        _delete_file(old.photo)

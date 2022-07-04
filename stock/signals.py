from django.db.models.signals import post_save
from django.dispatch import receiver

from stock.models import Currency


@receiver(post_save, sender=Currency)
def save_currency(sender, instance, created, **kwargs):
    if created:
        print(instance)

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.wallet.models import Wallet


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    """Crear automaticamente una billetera cuando se crea un usuario nuevo."""
    if created:
        Wallet.objects.get_or_create(user=instance)

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Consulte

@receiver(post_save, sender=Consulte)
def ch_created(sender, instance, created, **kwargs):
	if created:
		print('created')


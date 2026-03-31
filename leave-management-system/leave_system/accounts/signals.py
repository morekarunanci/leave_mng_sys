from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from leaves.models import LeaveBalance

User = get_user_model()

@receiver(post_save, sender=User)
def create_leave_balance(sender, instance, created, **kwargs):
    if created:
        LeaveBalance.objects.create(user=instance)
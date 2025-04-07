# signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Property
from .emails import property_create_email, property_status_change_email, email_interested_users

User = get_user_model()

@receiver(post_save, sender=Property)
def email_superadmins_on_create(sender, instance, created, **kwargs):
    if created:
        superadmins = User.objects.filter(is_superuser=True, email__isnull=False)
        emails = [admin.email for admin in superadmins]
        if emails:
            property_create_email(instance.title, emails)


@receiver(pre_save, sender=Property)
def notify_owner_on_status_change(sender, instance, **kwargs):
    try:
        old_instance = Property.objects.get(pk=instance.pk)
    except Property.DoesNotExist:
        return  # New object; nothing to compare

    if old_instance.status != instance.status:
        user_email = instance.user.email
        if user_email:
            property_status_change_email(instance.title, instance.status, user_email)


@receiver(pre_save, sender=Property)
def notify_on_approval(sender, instance, **kwargs):
    if not instance.pk:
        return  # It's a new object, not updated yet

    previous = Property.objects.get(pk=instance.pk)
    
    # Only trigger if status changed to approved
    if previous.status != 'approved' and instance.status == 'approved':
        email_interested_users(instance)
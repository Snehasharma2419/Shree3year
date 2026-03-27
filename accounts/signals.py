from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import User, UniversityID


@receiver(post_delete, sender=User)
def reset_university_id(sender, instance, **kwargs):
    """
    When a User is deleted, mark the associated UniversityID as unused.
    """
    if instance.university_id:
        UniversityID.objects.filter(
            university_id=instance.university_id
        ).update(is_used=False)

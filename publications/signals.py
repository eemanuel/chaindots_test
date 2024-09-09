from django.db.models.signals import post_save
from django.dispatch import receiver

from publications.models import Publication, PublicationComment

__all__ = (
    "update_user_publications_count",
    "update_user_comments_count",
)


@receiver(post_save, sender=Publication)
def update_user_publications_count(sender, instance, created, **kwargs):
    if created:
        instance.author.publications_count += 1
        try:
            instance.author.save(update_fields=["publications_count"])
        except Exception as exc:
            print(f"Signal 'update_user_publications_count' error: {exc}")


@receiver(post_save, sender=PublicationComment)
def update_user_comments_count(sender, instance, created, **kwargs):
    if created:
        instance.author.comments_count += 1
        try:
            instance.author.save(update_fields=["comments_count"])
        except Exception as exc:
            print(f"Signal 'update_user_publications_count' error: {exc}")

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField, ManyToManyField, PositiveIntegerField

from utils.models import TimeStampModel

__all__ = ("User",)


class User(TimeStampModel, AbstractUser):
    email = EmailField(unique=True, db_index=True)
    username = CharField(
        max_length=50,
        blank=False,
        unique=True,  # with unique=True "username" is indexed in the DB
    )
    password = CharField(max_length=100, blank=False)
    following = ManyToManyField("self", symmetrical=False, related_name="followers", blank=True)
    publications_count = PositiveIntegerField(
        default=0,
        help_text=(
            "Each time a Publication is created, this field is actuallized. "
            "Check signal 'publications.update_user_publications_count'"
        ),
    )
    comments_count = PositiveIntegerField(
        default=0,
        help_text=(
            "Each time a PublicationComment is created, this field is actuallized. "
            "Check signal 'publications.update_user_comments_count'"
        ),
    )

    groups = None  # remove AbstractUser.groups field
    user_permissions = None  # remove AbstractUser.user_permissions field

from django.db.models import DateTimeField, Model


class TimeStampModel(Model):
    created = DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True  # This model will then not be used to create any database table.

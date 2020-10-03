from django.db import models


class TimeStamped(models.Model):
    """ Abstract model with dates of creation and last update of the object """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NameTranslation(models.Model):
    """ Name field translation abstract model """

    name = models.CharField(max_length=500, blank=False, null=False)
    name_ru = models.CharField(max_length=500, blank=False, null=False)

    class Meta:
        abstract = True

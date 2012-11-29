from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()

    def __unicode__(self):
        return self.name

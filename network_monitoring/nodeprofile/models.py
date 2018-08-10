from django.db import models


# Create your models here.
class NodeProfile(models.Model):
    ip = models.GenericIPAddressField()
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=255)

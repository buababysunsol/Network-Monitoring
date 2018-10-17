from django.db import models


# Create your models here.
class NodeProfile(models.Model):
    ip = models.GenericIPAddressField()
    hostname = models.CharField(max_length=100)
    sitename = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

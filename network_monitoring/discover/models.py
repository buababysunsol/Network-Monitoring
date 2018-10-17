
from django.db import models
from djongo import models


class NodeIP(models.Model):
    ip = models.GenericIPAddressField()
    alive = models.BooleanField()
    site_name = models.CharField(max_length=255, blank=True)
    hostname = models.CharField(max_length=255, blank=True)
    community = models.CharField(max_length=250, blank=True)
    snmp_version = models.CharField(max_length=10, blank=True)
    software_image = models.CharField(max_length=255, blank=True)
    dns = models.CharField(max_length=255, blank=True)
    uptime = models.CharField(max_length=255, blank=True)
    interfaces = models.ListField(blank=True)

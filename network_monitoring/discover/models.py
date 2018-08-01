from django.db import models


class NodeIP(models.Model):
    ip = models.GenericIPAddressField()
    alive = models.BooleanField()

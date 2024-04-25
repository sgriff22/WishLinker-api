from django.db import models


class Priority(models.Model):
    name = models.CharField(max_length=255)

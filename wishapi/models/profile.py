from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="profile", blank=True, null=True)
    icon = models.IntegerField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)

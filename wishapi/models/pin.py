from django.db import models
from wishapi.models import Wishlist
from django.contrib.auth.models import User


class Pin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pins")
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="pins"
    )

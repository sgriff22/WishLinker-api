from django.db import models
from django.contrib.auth.models import User
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE


class Wishlist(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    spoil_surprises = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    date_of_event = models.DateTimeField(blank=True, null=True)
    pinned = models.BooleanField(default=False)

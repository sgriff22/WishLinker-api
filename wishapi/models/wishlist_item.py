from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE
from .priority import Priority
from .wishlist import Wishlist


class WishlistItem(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE

    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items_in_list"
    )
    name = models.CharField(max_length=255)
    note = models.CharField(max_length=255, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    quantity = models.IntegerField(default=1)
    priority = models.ForeignKey(
        Priority, on_delete=models.SET_NULL, blank=True, null=True
    )
    creation_date = models.DateTimeField(auto_now_add=True)

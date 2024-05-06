from django.db import models
from wishapi.models import WishlistItem
from django.contrib.auth.models import User


class Purchase(models.Model):
    wishlist_item = models.ForeignKey(
        WishlistItem, on_delete=models.CASCADE, related_name="purchased_item"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    purchase_date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)

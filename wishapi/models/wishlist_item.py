from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE
from .priority import Priority
from .wishlist import Wishlist
from django.db.models import Sum


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

    @property
    def leftover_quantity(self):
        # Calculate total purchased quantity
        total_purchased_quantity = (
            self.purchased_item.aggregate(total_quantity=Sum("quantity"))[
                "total_quantity"
            ]
            or 0
        )

        return self.quantity - total_purchased_quantity
    
    @property
    def purchase_quantity(self):
        # Calculate total purchased quantity
        total_purchased_quantity = (
            self.purchased_item.aggregate(total_quantity=Sum("quantity"))[
                "total_quantity"
            ]
            or 0
        )

        return total_purchased_quantity


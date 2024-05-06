from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from wishapi.models import Purchase, WishlistItem
from django.contrib.auth.models import User


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ["id", "wishlist_item", "user", "purchase_date", "quantity"]


class PurchaseViewSet(viewsets.ViewSet):
    """View for interacting with item purchases"""

    def create(self, request):
        """
        Create a new purchase.

        @api {POST} /purchases Create Purchase
        @apiName CreatePurchase
        @apiGroup Purchases

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiParam {Number} wishlist_item Wishlist item ID.
        @apiParam {Number} quantity Quantity of the item.

        @apiSuccess {Number} id Purchase ID.
        @apiSuccess {Number} wishlist_item Wishlist item ID.
        @apiSuccess {Number} user User ID.
        @apiSuccess {String} purchase_date Purchase date and time (ISO 8601 format).
        @apiSuccess {Number} quantity Quantity of the item.

        @apiSuccessExample {json} Success:
            HTTP/1.1 201 Created
            {
                "id": 1,
                "wishlist_item": 1,
                "user": 1,
                "purchase_date": "2024-05-03T12:00:00Z",
                "quantity": 2
            }
        """

        wishlist_item_id = request.data.get("wishlist_item")
        try:
            item = WishlistItem.objects.select_for_update().get(pk=wishlist_item_id)

        except:
            return Response(
                {"error": "Wishlist item not found"}, status=status.HTTP_404_NOT_FOUND
            )

        purchase = Purchase()
        purchase.wishlist_item = item
        purchase.user = request.auth.user
        purchase.quantity = request.data.get("quantity")

        try:
            purchase.save()

            serializer = PurchaseSerializer(purchase, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from wishapi.models import Purchase, WishlistItem, Wishlist
from django.contrib.auth.models import User
from wishapi.views import UserSerializer


class WishlistSerializer(serializers.ModelSerializer):
    """JSON serializer for public wishlists"""

    user = UserSerializer()

    class Meta:
        model = Wishlist
        fields = (
            "id",
            "title",
            "user",
        )


class ItemSerializer(serializers.ModelSerializer):
    wishlist = WishlistSerializer()

    class Meta:
        model = WishlistItem
        fields = ["id", "name", "wishlist", "website_url"]


class PurchaseSerializer(serializers.ModelSerializer):
    wishlist_item = ItemSerializer()

    class Meta:
        model = Purchase
        fields = ["id", "user", "purchase_date", "quantity", "wishlist_item"]


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

    def list(self, request):
        """
        Retrieve all purchases for the authenticated user.

        @api {GET} /purchases List Purchases
        @apiName ListPurchases
        @apiGroup Purchases

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiSuccess {Object[]} purchases List of purchases.
        @apiSuccess {Number} purchases.id Purchase ID.
        @apiSuccess {Number} purchases.wishlist_item Wishlist item ID.
        @apiSuccess {Number} purchases.user User ID.
        @apiSuccess {String} purchases.purchase_date Purchase date and time (ISO 8601 format).
        @apiSuccess {Number} purchases.quantity Quantity of the item.

        @apiSuccessExample {json} Success:
            HTTP/1.1 200 OK
        [
            {
                "id": 1,
                "user": 1,
                "purchase_date": "2024-05-08T03:47:13.742423Z",
                "quantity": 1,
                "wishlist_item": {
                    "id": 8,
                    "name": "Decorative Throw Pillow Covers",
                    "wishlist": {
                        "id": 5,
                        "title": "Jenna's Housewarming Party",
                        "user": {
                            "id": 3,
                            "username": "jenna@solis.com",
                            "first_name": "Jenna",
                            "last_name": "Solis"
                        }
                    }
                }
            }
        ]
        """
        purchases = Purchase.objects.filter(user=request.auth.user)
        serializer = PurchaseSerializer(
            purchases, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Delete a purchase.

        @api {DELETE} /purchases/:id Delete Purchase
        @apiName DeletePurchase
        @apiGroup Purchases

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiParam {Number} id Purchase ID.

        @apiSuccessExample {json} Success:
            HTTP/1.1 204 No Content
        """
        try:
            purchase = Purchase.objects.get(pk=pk)
            if purchase.user != request.auth.user:
                return Response(
                    {"error": "You don't have permission to delete this purchase"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            purchase.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Purchase.DoesNotExist:
            return Response(
                {"error": "Purchase not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

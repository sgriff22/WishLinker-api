from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import serializers, status
from django.contrib.auth.models import User
from wishapi.models import WishlistItem, Wishlist, Priority


class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "wishlist",
            "name",
            "note",
            "website_url",
            "quantity",
            "priority",
            "creation_date",
        ]


class WishlistItemViewSet(viewsets.ViewSet):
    """View for interacting with user wishlists"""

    def create(self, request):
        """
        Create a new wishlist item.

        @api {POST} /wishlist_items Create Wishlist item
        @apiName CreateWishlistItem
        @apiGroup Wishlists

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiParam {Number} wishlist Wishlist ID.
        @apiParam {String} name Name of the item.
        @apiParam {Number} [quantity=1] Quantity of the item (default: 1).
        @apiParam {String} [website_url] Website URL of the item.
        @apiParam {String} [note] Note for the item.
        @apiParam {Number} [priority] Priority level ID of the item.

        @apiSuccess {Number} id Wishlist item ID.
        @apiSuccess {Number} wishlist Wishlist ID.
        @apiSuccess {String} name Name of the item.
        @apiSuccess {Number} quantity Quantity of the item.
        @apiSuccess {String} website_url Website URL of the item.
        @apiSuccess {String} note Note for the item.
        @apiSuccess {Number} priority Priority level ID of the item.
        @apiSuccess {String} creation_date Date the wishlist item was created (ISO 8601 format).

        @apiSuccessExample {json} Success:
            HTTP/1.1 201 Created
            {
                "id": 1,
                "wishlist": 1,
                "name": "Example Item",
                "quantity": 2,
                "website_url": "https://example.com",
                "note": "This is a note for the item",
                "priority": 1,
                "creation_date": "2024-05-03T12:00:00Z"
            }
        """

        wishlist_id = request.data.get("wishlist")
        wishlist = Wishlist.objects.get(pk=wishlist_id)

        priority_id = request.data.get("priority")
        priority = Priority.objects.get(pk=priority_id)

        new_item = WishlistItem()
        # Get the data from the client's JSON payload
        new_item.wishlist = wishlist
        new_item.name = request.data.get("name")
        new_item.quantity = request.data.get("quantity")
        new_item.website_url = request.data.get("website_url")
        new_item.note = request.data.get("note")
        new_item.priority = priority

        try:

            new_item.save()

            serializer = WishlistItemSerializer(new_item, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

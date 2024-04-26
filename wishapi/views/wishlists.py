from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth.models import User
from wishapi.models import Wishlist
from django.http import HttpResponseServerError
from django.db.models import Q


class WishlistSerializer(serializers.ModelSerializer):
    """JSON serializer for public wishlists"""

    class Meta:
        model = Wishlist
        fields = (
            "id",
            "user",
            "title",
            "description",
            "spoil_surprises",
            "address",
            "creation_date",
            "date_of_event",
            "pinned",
        )


class WishlistViewSet(viewsets.ViewSet):
    """View for interacting with user wishlists"""

    def list(self, request):
        """
        @api {GET} /wishlists GET user's wishlists
        @apiName GetWishlists
        @apiGroup Wishlists

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} payment_id Query param to filter by payment used

        @apiSuccess (200) {Object[]} public_wishlists Array of public wishlist objects
        @apiSuccess (200) {id} public_wishlists.id Wishlist id
        @apiSuccess (200) {Number} public_wishlists.user User id associated with the wishlist
        @apiSuccess (200) {String} public_wishlists.title Title of the wishlist
        @apiSuccess (200) {String} public_wishlists.description Description of the wishlist
        @apiSuccess (200) {Boolean} public_wishlists.spoil_surprises Flag indicating whether surprises should be spoiled
        @apiSuccess (200) {String} public_wishlists.address Mailing address for purchased items associated with the wishlist
        @apiSuccess (200) {String} public_wishlists.creation_date Date the wishlist was created (ISO 8601 format)
        @apiSuccess (200) {String} public_wishlists.date_of_event Date of the event associated with the wishlist (ISO 8601 format)
        @apiSuccess (200) {Boolean} public_wishlists.pinned Flag indicating whether the wishlist is pinned

        @apiSuccess (200) {Object[]} private_wishlists Array of private wishlist objects
        @apiSuccess (200) {id} private_wishlists.id Wishlist id
        @apiSuccess (200) {Number} private_wishlists.user User id associated with the wishlist
        @apiSuccess (200) {String} private_wishlists.title Title of the wishlist
        @apiSuccess (200) {String} private_wishlists.description Description of the wishlist
        @apiSuccess (200) {Boolean} private_wishlists.spoil_surprises Flag indicating whether surprises should be spoiled
        @apiSuccess (200) {String} private_wishlists.address Mailing address for purchased items associated with the wishlist
        @apiSuccess (200) {String} private_wishlists.creation_date Date the wishlist was created (ISO 8601 format)
        @apiSuccess (200) {String} private_wishlists.date_of_event Date of the event associated with the wishlist (ISO 8601 format)
        @apiSuccess (200) {Boolean} private_wishlists.pinned Flag indicating whether the wishlist is pinned

        @apiSuccessExample {json} Success
            {
              "public": [
                {
                  "id": 3,
                  "user": 2,
                  "title": "Meg and Ryan's Wedding",
                  "description": "We are broke college students. Anything you can contribute would greatly appreciated!",
                  "spoil_surprises": true,
                  "address": "789 Oak Street, Silverwood, TX 75001",
                  "creation_date": "2024-04-26T08:00:00Z",
                  "date_of_event": "2024-05-10T08:00:00Z",
                  "pinned": false
                }
              ],
              "private": [
                {
                  "id": 4,
                  "user": 2,
                  "title": "My Birthday Wishlist",
                  "description": "Looking forward to some surprises!",
                  "spoil_surprises": false,
                  "address": "123 Elm Street, Springfield, IL 62701",
                  "creation_date": "2024-04-28T08:00:00Z",
                  "date_of_event": "2024-06-15T08:00:00Z",
                  "pinned": true
                }
              ]
            }
        """
        search_text = request.query_params.get("q", None)
        try:
            user = request.auth.user
            if search_text:
                public_wishlists = Wishlist.objects.filter(
                    Q(title__contains=search_text)
                    | Q(description__contains=search_text),
                    private=False,
                    user=user,
                )
                private_wishlists = Wishlist.objects.filter(
                    Q(title__contains=search_text)
                    | Q(description__contains=search_text),
                    private=True,
                    user=user,
                )
            else:
                public_wishlists = Wishlist.objects.filter(private=False, user=user)
                private_wishlists = Wishlist.objects.filter(private=True, user=user)

            public_serializer = WishlistSerializer(
                public_wishlists, many=True, context={"request": request}
            )
            private_serializer = WishlistSerializer(
                private_wishlists, many=True, context={"request": request}
            )

            return Response(
                {
                    "public": public_serializer.data,
                    "private": private_serializer.data,
                }
            )

        except Exception as ex:
            return HttpResponseServerError(ex)

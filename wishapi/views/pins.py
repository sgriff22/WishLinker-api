from django.db import models
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status, serializers
from wishapi.models import Pin, Wishlist
from wishapi.views import UserSerializer


class WishlistSerializer(serializers.ModelSerializer):
    """JSON serializer for public wishlists"""

    user = UserSerializer()

    class Meta:
        model = Wishlist
        fields = (
            "id",
            "user",
            "title",
            "description",
            "creation_date",
            "date_of_event",
        )


class PinSerializer(serializers.ModelSerializer):
    wishlist = WishlistSerializer()

    class Meta:
        model = Pin
        fields = ["id", "user", "wishlist"]


class PinViewSet(viewsets.ViewSet):
    """View for interacting with wishlist pins to homepage"""

    def create(self, request):
        """
        Create a new pin.

        @api {POST} /pins Create Pin
        @apiName CreatePin
        @apiGroup Pins

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiParam {Number} wishlist Wishlist ID.

        @apiSuccess {Number} id Pin ID.
        @apiSuccess {Number} user User ID.
        @apiSuccess {Number} wishlist Wishlist ID.

        @apiSuccessExample {json} Success:
            HTTP/1.1 201 Created
            {
                "id": 1,
                "user": 1,
                "wishlist": 1
            }
        """
        wishlist_id = request.data.get("wishlist")

        try:
            wishlist = Wishlist.objects.get(pk=wishlist_id)
        except Wishlist.DoesNotExist:
            return Response(
                {"error": "Wishlist not found"}, status=status.HTTP_404_NOT_FOUND
            )

        pin = Pin()
        pin.user = request.user
        pin.wishlist = wishlist

        try:
            pin.save()
            serializer = PinSerializer(pin)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        List all pins.

        @api {GET} /pins List Pins
        @apiName ListPins
        @apiGroup Pins

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiSuccess {Object[]} pins List of pins
        @apiSuccess {Number} pins.id Pin ID.
        @apiSuccess {Number} pins.user User ID.
        @apiSuccess {Number} pins.wishlist Wishlist ID.

        @apiSuccessExample {json} Success:
            HTTP/1.1 200 OK
           [
                {
                    "id": 1,
                    "user": 2,
                    "wishlist": {
                        "id": 1,
                        "user": {
                            "id": 1,
                            "username": "ryan@ryantanay.com",
                            "first_name": "Ryan",
                            "last_name": "Tanay"
                        },
                        "title": "My 40th Birthday",
                        "description": "I am turning 40! Here are a few things I like",
                        "creation_date": "2024-04-26T08:00:00Z",
                        "date_of_event": "2024-05-10T08:00:00Z"
                    }
                },
            ]
        """
        try:
            pins = Pin.objects.filter(user=request.user)
            serializer = PinSerializer(pins, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """
        Delete a pinned wishlist.

        @api {DELETE} /pins/:id Delete Pin
        @apiName DeletePin
        @apiGroup Pins

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization:
            Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiParam {Number} id Pin ID.

        @apiSuccessExample {json} Success:
            HTTP/1.1 204 No Content
        """
        try:
            pin = Pin.objects.get(pk=pk)
            if pin.user != request.auth.user:
                return Response(
                    {"error": "You don't have permission to delete this pin"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            pin.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Pin.DoesNotExist:
            return Response(
                {"error": "Pin not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

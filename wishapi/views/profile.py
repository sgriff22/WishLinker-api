from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import viewsets
from wishapi.models import Wishlist, Friend
from wishapi.views import UserSerializer
from django.db.models import Q


class WishlistSerializer(serializers.ModelSerializer):
    """JSON serializer for wishlists"""

    class Meta:
        model = Wishlist
        fields = (
            "id",
            "title",
            "description",
            "creation_date",
            "date_of_event",
        )


class FriendSerializer(serializers.ModelSerializer):
    """JSON serializer for friends"""

    friend_info = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = ("id", "friend_info")

    def get_friend_info(self, obj):
        # Get the request's user
        request_user = self.context.get("request").user

        # Get the requested user profile from the context
        viewed_user = self.context.get("requested_profile")

        # Determine which user is the friend
        if viewed_user:
            # If viewed_user is available (when retrieving another user's profile)
            friend_user = obj.user1 if viewed_user != obj.user1 else obj.user2
        else:
            # If viewed_user is not available (when retrieving the authenticated user's profile)
            friend_user = obj.user1 if request_user != obj.user1 else obj.user2

        friend_user_serializer = UserSerializer(friend_user)
        return friend_user_serializer.data


class ProfileViewSet(viewsets.ViewSet):
    """Request handlers for user profile info in the WishLinker Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        """
        Get current user's profile, including their wishlists and friends.

        @api {GET} /profile get current User Profile
        @apiName GetUserProfile
        @apiGroup Profiles
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization: Token d74b97fbe905134520bb236b0016703f50380dcf

        @apiSuccess {Object} user User's information.
        @apiSuccess {Number} user.id User ID.
        @apiSuccess {String} user.username User's username (email).
        @apiSuccess {String} user.first_name User's first name.
        @apiSuccess {String} user.last_name User's last name.

        @apiSuccess {Object[]} wishlists Array of wishlists associated with the user.
        @apiSuccess {Number} wishlists.id Wishlist ID.
        @apiSuccess {String} wishlists.title Wishlist title.
        @apiSuccess {String} wishlists.description Wishlist description.
        @apiSuccess {String} wishlists.creation_date Date the wishlist was created (ISO 8601 format).
        @apiSuccess {String} wishlists.date_of_event Date of the event associated with the wishlist (ISO 8601 format).

        @apiSuccess {Object[]} friends Array of friends associated with the user.
        @apiSuccess {Number} friends.id Friend ID.
        @apiSuccess {Object} friends.friend_info Information about the friend.
        @apiSuccess {Number} friends.friend_info.id Friend's user ID.
        @apiSuccess {String} friends.friend_info.username Friend's username (email).
        @apiSuccess {String} friends.friend_info.first_name Friend's first name.
        @apiSuccess {String} friends.friend_info.last_name Friend's last name.

        @apiSuccessExample {json} Success:
        HTTP/1.1 200 OK
        {
            "user": {
                "id": 1,
                "username": "ryan@ryantanay.com",
                "first_name": "Ryan",
                "last_name": "Tanay"
            },
            "wishlists": [
                {
                    "id": 1,
                    "title": "My Birthday 40th birthday",
                    "description": "I am turning 40! Here are a few things I like",
                    "creation_date": "2024-04-26T08:00:00Z",
                    "date_of_event": "2024-05-10T08:00:00Z"
                }
            ],
            "friends": [
                {
                    "id": 1,
                    "friend_info": {
                        "id": 2,
                        "username": "meg@ducharme.com",
                        "first_name": "Meg",
                        "last_name": "Ducharme"
                    }
                },
                {
                    "id": 6,
                    "friend_info": {
                        "id": 6,
                        "username": "tyler@hilliard.com",
                        "first_name": "Tyler",
                        "last_name": "Hilliard"
                    }
                }
            ]
        }
        """

        try:
            user = request.auth.user

            # Retrieve wishlists associated with the user
            wishlists = Wishlist.objects.filter(user=user, private=False)
            wishlist_serializer = WishlistSerializer(wishlists, many=True)

            # Retrieve friends associated with the user
            friends = Friend.objects.filter(
                Q(user1_id=user.id) | Q(user2_id=user.id), accepted=True
            )
            friend_serializer = FriendSerializer(
                friends, many=True, context={"request": request}
            )

            # Retrieve friend requests associated with the user
            friend_requests = Friend.objects.filter(
                Q(user1_id=user.id) | Q(user2_id=user.id), accepted=False
            )
            friend_request_serializer = FriendSerializer(
                friend_requests,
                many=True,
                context={
                    "request": request,
                },
            )

            user_serializer = UserSerializer(user)

            # Combine all serialized data into a single response
            response_data = {
                "user": user_serializer.data,
                "wishlists": wishlist_serializer.data,
                "friends": friend_serializer.data,
                "friend_requests": friend_request_serializer.data,
            }

            return Response(response_data)

        except User.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(str(ex))

    def retrieve(self, request, pk=None):
        """
        Retrieve a user's profile by their ID, including their wishlists and friends.

        @api {GET} /profile/:id Retrieve User Profile
        @apiName RetrieveUserProfile
        @apiGroup Profiles
        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization: Token d74b97fbe905134520bb236b0016703f50380dcf
        @apiParam {Number} pk User's unique ID.

        @apiSuccess {Object} user User's information.
        @apiSuccess {Number} user.id User ID.
        @apiSuccess {String} user.username User's username (email).
        @apiSuccess {String} user.first_name User's first name.
        @apiSuccess {String} user.last_name User's last name.

        @apiSuccess {Object[]} wishlists Array of wishlists associated with the user.
        @apiSuccess {Number} wishlists.id Wishlist ID.
        @apiSuccess {String} wishlists.title Wishlist title.
        @apiSuccess {String} wishlists.description Wishlist description.
        @apiSuccess {String} wishlists.creation_date Date the wishlist was created (ISO 8601 format).
        @apiSuccess {String} wishlists.date_of_event Date of the event associated with the wishlist (ISO 8601 format).

        @apiSuccess {Object[]} friends Array of friends associated with the user.
        @apiSuccess {Number} friends.id Friend ID.
        @apiSuccess {Object} friends.friend_info Information about the friend.
        @apiSuccess {Number} friends.friend_info.id Friend's user ID.
        @apiSuccess {String} friends.friend_info.username Friend's username (email).
        @apiSuccess {String} friends.friend_info.first_name Friend's first name.
        @apiSuccess {String} friends.friend_info.last_name Friend's last name.

        @apiSuccessExample {json} Success:
        HTTP/1.1 200 OK
        {
            "user": {
                "id": 1,
                "username": "ryan@ryantanay.com",
                "first_name": "Ryan",
                "last_name": "Tanay"
            },
            "wishlists": [
                {
                    "id": 1,
                    "title": "My Birthday 40th birthday",
                    "description": "I am turning 40! Here are a few things I like",
                    "creation_date": "2024-04-26T08:00:00Z",
                    "date_of_event": "2024-05-10T08:00:00Z"
                }
            ],
            "friends": [
                {
                    "id": 1,
                    "friend_info": {
                        "id": 2,
                        "username": "meg@ducharme.com",
                        "first_name": "Meg",
                        "last_name": "Ducharme"
                    }
                },
                {
                    "id": 6,
                    "friend_info": {
                        "id": 6,
                        "username": "tyler@hilliard.com",
                        "first_name": "Tyler",
                        "last_name": "Hilliard"
                    }
                }
            ]
        }
        """

        try:
            # Retrieve the user based on the primary key (pk)
            user = User.objects.get(pk=pk)

            # Retrieve wishlists associated with the user
            wishlists = Wishlist.objects.filter(user=user, private=False)
            wishlist_serializer = WishlistSerializer(wishlists, many=True)

            # Retrieve friends associated with the user
            friends = Friend.objects.filter(
                Q(user1_id=user.id) | Q(user2_id=user.id), accepted=True
            )

            requested_user_profile = User.objects.get(pk=pk)

            friend_serializer = FriendSerializer(
                friends,
                many=True,
                context={
                    "request": request,
                    "requested_profile": requested_user_profile,
                },
            )

            user_serializer = UserSerializer(user)

            # Combine all serialized data into a single response
            response_data = {
                "user": user_serializer.data,
                "wishlists": wishlist_serializer.data,
                "friends": friend_serializer.data,
            }

            return Response(response_data)

        except User.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(str(ex))

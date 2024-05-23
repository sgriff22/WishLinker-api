from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework import status
from wishapi.models import Friend, Profile
from django.contrib.auth.models import User
from wishapi.views import UserSerializer
from django.db.models import Q, Value, Case, When, IntegerField
from rest_framework.decorators import action


class ProfileImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("image",)


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ["id", "user1", "user2", "accepted"]


class FriendViewSet(viewsets.ViewSet):
    """View for interacting with user friends"""

    def update(self, request, pk=None):
        """
        @api {PUT} /friends/:id PUT accepted value for friends
        @apiName UpdateFriend
        @apiGroup Friends

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {Number} id Friend ID (route parameter)
        @apiParam {Boolean} accepted Accepted status for the friend request
        @apiParamExample {json} Input
            {
                "accepted": true
            }

        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """

        accepted_value = request.data.get("accepted")

        try:
            friend = Friend.objects.get(pk=pk)
        except Friend.DoesNotExist:
            return Response(
                "Friend instance not found", status=status.HTTP_404_NOT_FOUND
            )

        friend.accepted = accepted_value
        friend.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /friends/:id DELETE friend instance
        @apiName UnFriend
        @apiGroup Friends

        @apiParam {Number} id Friend's ID (route parameter) to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """

        try:
            friend = Friend.objects.get(pk=pk)
        except Friend.DoesNotExist:
            return Response(
                "Friend instance not found", status=status.HTTP_404_NOT_FOUND
            )

        friend.delete()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        """
        @api {POST} /friends Create a new friend instance
        @apiName CreateFriend
        @apiGroup Friends

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {Number} user_id ID of the user to send friend request
        @apiParamExample {json} Input
            {
                "user_id": 123
            }

        @apiSuccessExample {json} Success
            HTTP/1.1 201 Created
            {
                "id": 8,
                "user1_id": 1,
                "user2_id": 2,
                "accepted": false
            }
        """

        try:
            # Get the current user
            user = request.user

            # Get the user_id from the request data
            user_id = request.data.get("user_id")

            # Retrieve the User instance corresponding to user_id
            friend_user = User.objects.get(pk=user_id)

            # Create a new Friend instance
            new_friend = Friend.objects.create(
                user1=user, user2=friend_user, accepted=False
            )

            serializer = FriendSerializer(new_friend, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response(
                {"error": "User instance not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def get_all_users(self, request):
        """
        Get all users in the database, excluding the current user and the user's friends.
        """
        current_user = request.user

        # Retrieve the IDs of the user's friends
        friend_ids = Friend.objects.filter(
            Q(user1=current_user, accepted=True) | Q(user2=current_user, accepted=True)
        ).values_list("user1_id", "user2_id")

        # Extract all friend IDs into a single list
        all_friend_ids = [
            friend_id for friend_pair in friend_ids for friend_id in friend_pair
        ]

        # Get IDs of users to whom the current user has sent friend requests
        friend_requests_sent = Friend.objects.filter(
            user1=current_user, accepted=False
        ).values_list("user2_id", flat=True)

        # Get IDs of users to whom the current user has sent friend requests
        friend_requests_received = Friend.objects.filter(
            user2=current_user, accepted=False
        ).values_list("user1_id", flat=True)

        # Exclude the current user and the user's friends from the query
        users = User.objects.exclude(Q(id=current_user.id) | Q(id__in=all_friend_ids))

        # Filter friends by name if search query is provided
        search_query = request.query_params.get("q", None)
        if search_query:
            users = users.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(username__icontains=search_query)
            )

        serialized_users = []
        for user in users:
            serialized_user = UserSerializer(user).data
            # Check if the user has already received a friend request from the current user
            friend_request_sent = user.id in friend_requests_sent
            serialized_user["friend_request_sent"] = friend_request_sent
            friend_request_received = user.id in friend_requests_received
            serialized_user["friend_request_received"] = friend_request_received
            # Append the profile image to the serialized user
            try:
                profile = Profile.objects.get(user=user)

            except Profile.DoesNotExist:
                profile = None

            serialized_user["profile"] = ProfileImageSerializer(profile).data
            serialized_users.append(serialized_user)

        return Response(serialized_users)

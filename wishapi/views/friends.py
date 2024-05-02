from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from wishapi.models import Friend
from django.contrib.auth.models import User
from wishapi.views import UserSerializer
from django.db.models import Q
from rest_framework.decorators import action


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

        # Serialize the users and return the response
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

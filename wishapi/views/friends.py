from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from wishapi.models import Friend


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

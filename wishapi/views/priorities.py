from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import serializers
from wishapi.models import Priority


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ("id", "name")


class PriorityViewSet(viewsets.ViewSet):
    """View for interacting with item priority"""

    def list(self, request):
        """
        @api {GET} /priorities GET all the priority options
        @apiName GetPriorities
        @apiGroup Priorities

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611
        """

        priorities = Priority.objects.all()

        serializer = PrioritySerializer(
            priorities, many=True, context={"request": request}
        )
        return Response(serializer.data)

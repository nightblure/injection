from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from injection import Provide, inject
from tests.container_objects import Container


class PostEndpointBodySerializer(serializers.Serializer):
    key = serializers.IntegerField()


class View(APIView):
    @inject
    def get(self, _: Request, redis=Provide[Container.redis]):
        response_body = {"redis_url": redis.url}
        return Response(response_body, status=status.HTTP_200_OK)

    @inject
    def post(self, request: Request, redis=Provide[Container.redis]):
        body_serializer = PostEndpointBodySerializer(data=request.data)
        body_serializer.is_valid()
        key = body_serializer.validated_data["key"]
        response_body = {"redis_key": redis.get(key)}
        return Response(response_body, status=status.HTTP_201_CREATED)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView


class AliveView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request=None):
        return Response({"status": "OK"})


alive_view = AliveView.as_view()

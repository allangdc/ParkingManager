from datetime import datetime
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from parking import serializer
from parking.models import ParkingModels
from parking.serializer import ParkingSerializer

class ParkingViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ParkingSerializer
    queryset = ParkingModels.objects.all()

    @action(detail=False, methods=['get'], url_path="(?P<plate>[A-Z]{3}-[0-9]{4})")
    def search_plate(self, request, plate=None):
        data = self.get_queryset().filter(plate=plate)
        if len(data) > 0:
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        raise NotFound()

    @action(detail=True, methods=['put'])
    def pay(self, request, pk=None):
        obj = self.get_object()
        obj.paid = True
        obj.save()
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['put'])
    def out(self, request, pk=None):
        obj = self.get_object()
        obj.departure_time = datetime.now()
        try:
            obj.full_clean()
            obj.save()
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
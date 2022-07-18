from django.urls import path
from parking.views import ParkingViewSet
from rest_framework.routers import SimpleRouter

parking_router = SimpleRouter()
parking_router.register("", ParkingViewSet)

urlpatterns = [
]
